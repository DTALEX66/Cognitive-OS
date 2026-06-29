"""B-Line Observability - Distributed tracing, metrics, and structured logging.

Extends the existing ExecutionTraceEngine with:
- Span/Trace tree structures for distributed tracing
- MetricsCollector for latency, success rate, token usage
- LogExporter for structured JSON/text log output
- Dashboard-ready summary data for frontend consumption
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any
from collections import defaultdict
import json
import time
import threading
import uuid


@dataclass
class Span:
    """A single unit of work within a trace."""
    span_id: str
    trace_id: str
    parent_span_id: str = ""
    operation: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    status: str = "ok"
    tags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000 if self.end_time else 0


@dataclass
class Trace:
    """A distributed trace composed of multiple spans."""
    trace_id: str
    name: str = ""
    spans: list[Span] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    status: str = "ok"
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_span(self, span: Span) -> None:
        self.spans.append(span)

    def get_span(self, span_id: str) -> Span | None:
        for s in self.spans:
            if s.span_id == span_id:
                return s
        return None

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "name": self.name,
            "status": self.status,
            "duration_ms": (self.end_time - self.start_time) * 1000,
            "span_count": len(self.spans),
            "spans": [
                {
                    "span_id": s.span_id,
                    "parent_span_id": s.parent_span_id,
                    "operation": s.operation,
                    "duration_ms": s.duration_ms,
                    "status": s.status,
                    "tags": s.tags,
                    "events": s.events,
                }
                for s in self.spans
            ],
        }


@dataclass
class MetricPoint:
    """A single metric observation."""
    name: str
    value: float
    timestamp: float
    labels: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """Collects latency, success rate, and token usage metrics."""

    def __init__(self, window_sec: float = 3600.0) -> None:
        self._window_sec = window_sec
        self._lock = threading.Lock()
        self._metrics: dict[str, list[MetricPoint]] = defaultdict(list)
        self._counters: dict[str, int] = defaultdict(int)

    def record_latency(self, operation: str, duration_ms: float,
                       labels: dict[str, str] | None = None) -> None:
        self._add_metric("latency", operation, duration_ms, labels)

    def record_success(self, operation: str) -> None:
        with self._lock:
            self._counters[f"{operation}:success"] += 1
            self._counters[f"{operation}:total"] += 1

    def record_failure(self, operation: str) -> None:
        with self._lock:
            self._counters[f"{operation}:total"] += 1

    def record_tokens(self, operation: str, prompt_tokens: int,
                      completion_tokens: int,
                      labels: dict[str, str] | None = None) -> None:
        labels = labels or {}
        self._add_metric("prompt_tokens", operation, float(prompt_tokens), labels)
        self._add_metric("completion_tokens", operation, float(completion_tokens), labels)
        self._add_metric("total_tokens", operation,
                         float(prompt_tokens + completion_tokens), labels)

    def get_success_rate(self, operation: str = "") -> dict:
        with self._lock:
            total = self._counters.get(f"{operation}:total", 0)
            success = self._counters.get(f"{operation}:success", 0)
            return {
                "operation": operation,
                "total": total,
                "success": success,
                "failure": total - success,
                "rate": round(success / max(total, 1), 4),
            }

    def get_latency_stats(self, operation: str) -> dict:
        with self._lock:
            points = self._metrics.get(f"latency:{operation}", [])
            if not points:
                return {"operation": operation, "count": 0}
            values = sorted(p.value for p in points)
            return {
                "operation": operation,
                "count": len(values),
                "avg_ms": round(sum(values) / len(values), 2),
                "min_ms": round(values[0], 2),
                "max_ms": round(values[-1], 2),
                "p50_ms": round(_percentile(values, 50), 2),
                "p90_ms": round(_percentile(values, 90), 2),
                "p99_ms": round(_percentile(values, 99), 2),
            }

    def get_token_summary(self) -> dict:
        with self._lock:
            total_prompt = 0
            total_completion = 0
            for key, points in self._metrics.items():
                if key.startswith("prompt_tokens:"):
                    total_prompt += int(sum(mp.value for mp in points))
                elif key.startswith("completion_tokens:"):
                    total_completion += int(sum(mp.value for mp in points))
            return {
                "total_prompt_tokens": total_prompt,
                "total_completion_tokens": total_completion,
                "total_tokens": total_prompt + total_completion,
            }

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "latency": {
                    k.split(":", 1)[1]: self.get_latency_stats(k.split(":", 1)[1])
                    for k in self._metrics
                    if k.startswith("latency:")
                },
                "tokens": self.get_token_summary(),
            }

    def _add_metric(self, kind: str, operation: str, value: float,
                    labels: dict[str, str] | None) -> None:
        actual_labels = labels or {}
        actual_labels["_op"] = operation
        with self._lock:
            mp = MetricPoint(
                name=kind, value=value,
                timestamp=time.time(), labels=actual_labels,
            )
            key = f"{kind}:{operation}"
            self._metrics[key].append(mp)
            self._prune(key)

    def _prune(self, key: str) -> None:
        cutoff = time.time() - self._window_sec
        self._metrics[key] = [
            m for m in self._metrics[key] if m.timestamp >= cutoff
        ]


def _percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    idx = int(len(sorted_values) * pct / 100.0)
    idx = min(idx, len(sorted_values) - 1)
    return sorted_values[idx]


class LogExporter:
    """Exports structured logs and trace data to JSON or text formats."""

    def __init__(self, format_type: str = "json") -> None:
        self.format_type = format_type
        self._logs: list[dict] = []

    def log_event(self, level: str, message: str,
                  extra: dict[str, Any] | None = None) -> dict:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            **(extra or {}),
        }
        self._logs.append(entry)
        return entry

    def export_trace(self, trace: Trace, format_type: str = "") -> str:
        fmt = format_type or self.format_type
        data = trace.to_dict()
        if fmt == "json":
            return json.dumps(data, indent=2, default=str)
        else:
            return _trace_to_text(data)

    def export_logs(self, format_type: str = "", level: str = "") -> str:
        fmt = format_type or self.format_type
        entries = self._logs
        if level:
            entries = [e for e in entries if e.get("level") == level]
        if fmt == "json":
            return json.dumps(entries, indent=2, default=str)
        else:
            lines = []
            for e in entries:
                ts = e.get("timestamp", "")
                lvl = e.get("level", "")
                msg = e.get("message", "")
                extra = {k: v for k, v in e.items()
                         if k not in ("timestamp", "level", "message")}
                line = f"[{ts}] [{lvl.upper():<5}] {msg}"
                if extra:
                    line += f" | {json.dumps(extra, default=str)}"
                lines.append(line)
            return "\n".join(lines)

    def export_dashboard_summary(self, trace: Trace,
                                 metrics: MetricsCollector) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace": {
                "trace_id": trace.trace_id,
                "name": trace.name,
                "status": trace.status,
                "duration_ms": trace.to_dict()["duration_ms"],
                "span_count": len(trace.spans),
                "error_spans": sum(1 for s in trace.spans if s.status == "error"),
            },
            "metrics": {
                "success_rate": metrics.get_success_rate(),
                "tokens": metrics.get_token_summary(),
            },
            "spans_by_operation": _group_spans_by_operation(trace),
        }

    def clear(self) -> None:
        self._logs.clear()


def _trace_to_text(trace_dict: dict) -> str:
    lines = [
        f"Trace: {trace_dict['trace_id']} ({trace_dict['name']})",
        f"Status: {trace_dict['status']} | Duration: {trace_dict['duration_ms']:.1f}ms",
        f"Spans ({trace_dict['span_count']}):",
    ]
    for s in trace_dict.get("spans", []):
        pad = "  " if not s.get("parent_span_id") else "    "
        lines.append(
            f"{pad}[{s['span_id'][:8]}] {s['operation']} "
            f"({s['duration_ms']:.1f}ms) [{s['status']}]"
        )
    return "\n".join(lines)


def _group_spans_by_operation(trace: Trace) -> dict:
    groups: dict[str, list[dict]] = defaultdict(list)
    for s in trace.spans:
        groups[s.operation].append({
            "span_id": s.span_id,
            "duration_ms": s.duration_ms,
            "status": s.status,
        })
    return {
        op: {
            "count": len(spans),
            "avg_duration_ms": round(
                sum(x["duration_ms"] for x in spans) / len(spans), 2
            ),
            "errors": sum(1 for x in spans if x["status"] == "error"),
        }
        for op, spans in groups.items()
    }


class Tracer:
    """Orchestrates distributed tracing with span lifecycle management."""

    def __init__(self) -> None:
        self._traces: dict[str, Trace] = {}
        self._active_spans: dict[str, Span] = {}
        self.metrics = MetricsCollector()

    def start_trace(self, name: str, metadata: dict | None = None) -> Trace:
        trace_id = str(uuid.uuid4())
        trace = Trace(
            trace_id=trace_id, name=name,
            start_time=time.time(), metadata=metadata or {},
        )
        self._traces[trace_id] = trace
        return trace

    def start_span(self, operation: str, trace_id: str = "",
                   parent_span_id: str = "",
                   tags: dict | None = None,
                   metadata: dict | None = None) -> Span:
        if not trace_id:
            trace_id = str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        span = Span(
            span_id=span_id, trace_id=trace_id,
            parent_span_id=parent_span_id, operation=operation,
            start_time=time.time(), tags=tags or {}, metadata=metadata or {},
        )
        self._active_spans[span_id] = span
        if trace_id in self._traces:
            self._traces[trace_id].add_span(span)
        return span

    def end_span(self, span_id: str, status: str = "ok",
                 metadata: dict | None = None) -> Span | None:
        span = self._active_spans.pop(span_id, None)
        if span is None:
            return None
        span.end_time = time.time()
        span.status = status
        if metadata:
            span.metadata.update(metadata)
        self.metrics.record_latency(span.operation, span.duration_ms)
        if status == "error":
            self.metrics.record_failure(span.operation)
        else:
            self.metrics.record_success(span.operation)
        return span

    def end_trace(self, trace_id: str, status: str = "ok") -> Trace | None:
        trace = self._traces.get(trace_id)
        if trace is None:
            return None
        trace.end_time = time.time()
        trace.status = status
        return trace

    def get_trace(self, trace_id: str) -> Trace | None:
        return self._traces.get(trace_id)

    def get_span(self, span_id: str) -> Span | None:
        return self._active_spans.get(span_id)

    def list_traces(self, limit: int = 20) -> list[dict]:
        sorted_traces = sorted(
            self._traces.values(), key=lambda t: t.start_time, reverse=True,
        )
        return [t.to_dict() for t in sorted_traces[:limit]]

    def export_dashboard(self, trace_id: str = "") -> dict:
        exporter = LogExporter()
        if trace_id and trace_id in self._traces:
            trace = self._traces[trace_id]
        elif self._traces:
            trace = max(self._traces.values(), key=lambda t: t.start_time)
        else:
            return {"error": "no traces available"}
        return exporter.export_dashboard_summary(trace, self.metrics)


__all__ = [
    "Span", "Trace", "MetricPoint", "MetricsCollector",
    "LogExporter", "Tracer",
]
