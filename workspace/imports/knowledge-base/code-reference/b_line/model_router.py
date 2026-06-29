"""B-Line Model Router - Model registry, routing, fallback, and rate limiting.

Provides intelligent model selection based on task type, cost, and latency.
Includes token-bucket rate limiting and per-call cost tracking.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from collections import defaultdict
import threading
import time
import random


# ─────────────────────────────────────────
# Model Registry
# ─────────────────────────────────────────

@dataclass
class ModelInfo:
    """Metadata for a registered model."""
    name: str
    provider: str  # local | openai | anthropic | other
    cost_per_1k_prompt: float = 0.0
    cost_per_1k_completion: float = 0.0
    avg_latency_ms: float = 500.0
    max_tokens: int = 4096
    capabilities: list[str] = field(default_factory=list)
    available: bool = True
    priority: int = 10  # lower = higher priority

    def estimate_cost(self, prompt_tokens: int,
                      completion_tokens: int) -> float:
        return (
            (prompt_tokens / 1000) * self.cost_per_1k_prompt
            + (completion_tokens / 1000) * self.cost_per_1k_completion
        )


class ModelRegistry:
    """Registry of available models with metadata."""

    def __init__(self) -> None:
        self._models: dict[str, ModelInfo] = {}
        self._lock = threading.Lock()
        self._register_defaults()

    def _register_defaults(self) -> None:
        defaults = [
            ModelInfo(
                name="local-llama3", provider="local",
                cost_per_1k_prompt=0.0, cost_per_1k_completion=0.0,
                avg_latency_ms=300, max_tokens=8192,
                capabilities=["chat", "code", "summarize"], priority=1,
            ),
            ModelInfo(
                name="local-codellama", provider="local",
                cost_per_1k_prompt=0.0, cost_per_1k_completion=0.0,
                avg_latency_ms=400, max_tokens=4096,
                capabilities=["code", "fill"], priority=2,
            ),
            ModelInfo(
                name="openai-gpt4o", provider="openai",
                cost_per_1k_prompt=0.005, cost_per_1k_completion=0.015,
                avg_latency_ms=800, max_tokens=128_000,
                capabilities=["chat", "code", "reason", "summarize", "analyze"],
                priority=5,
            ),
            ModelInfo(
                name="openai-gpt4o-mini", provider="openai",
                cost_per_1k_prompt=0.00015, cost_per_1k_completion=0.0006,
                avg_latency_ms=400, max_tokens=128_000,
                capabilities=["chat", "code", "summarize"], priority=6,
            ),
            ModelInfo(
                name="anthropic-claude", provider="anthropic",
                cost_per_1k_prompt=0.003, cost_per_1k_completion=0.015,
                avg_latency_ms=1000, max_tokens=200_000,
                capabilities=["chat", "code", "reason", "analyze", "long_context"],
                priority=7,
            ),
        ]
        for m in defaults:
            self.register(m)

    def register(self, model: ModelInfo) -> None:
        with self._lock:
            self._models[model.name] = model

    def unregister(self, name: str) -> bool:
        with self._lock:
            if name in self._models:
                del self._models[name]
                return True
            return False

    def get(self, name: str) -> ModelInfo | None:
        with self._lock:
            return self._models.get(name)

    def list_models(self, provider: str = "",
                    capability: str = "",
                    available_only: bool = True) -> list[ModelInfo]:
        with self._lock:
            models = list(self._models.values())
            if provider:
                models = [m for m in models if m.provider == provider]
            if capability:
                models = [m for m in models if capability in m.capabilities]
            if available_only:
                models = [m for m in models if m.available]
            return sorted(models, key=lambda m: m.priority)

    def set_available(self, name: str, available: bool) -> bool:
        with self._lock:
            model = self._models.get(name)
            if model:
                model.available = available
                return True
            return False


# ─────────────────────────────────────────
# Router
# ─────────────────────────────────────────

@dataclass
class RouteDecision:
    """Result of a routing decision."""
    model_name: str
    provider: str
    estimated_cost: float
    estimated_latency_ms: float
    reason: str
    fallback_chain: list[str]


class Router:
    """Selects the best model based on task type, cost, and latency preferences.

    Supports:
    - Capability-based filtering
    - Cost-optimized routing (prefer cheapest capable model)
    - Latency-optimized routing (prefer fastest capable model)
    - Fallback chains when primary model fails
    - Provider affinity (stay within same provider family)
    """

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry
        self._failure_counts: dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()

    def route(self, task_type: str = "chat",
              prefer: str = "cost",  # cost | latency | quality
              required_capabilities: list[str] | None = None,
              excluded_models: list[str] | None = None,
              max_fallback: int = 2) -> RouteDecision:
        """Select the best model for a given task.

        Args:
            task_type: Type of task (chat, code, reason, summarize, etc.)
            prefer: Preference for routing: cost, latency, or quality
            required_capabilities: Extra capabilities beyond task_type
            excluded_models: Models to exclude from consideration
            max_fallback: Number of fallback models to include in chain
        """
        caps = [task_type] + (required_capabilities or [])
        candidates = self.registry.list_models(capability=task_type)

        excluded = set(excluded_models or [])
        with self._lock:
            candidates = [
                m for m in candidates
                if m.name not in excluded
                and self._failure_counts.get(m.name, 0) < 3
            ]

        if not candidates:
            return RouteDecision(
                model_name="", provider="",
                estimated_cost=0.0, estimated_latency_ms=0.0,
                reason="no_models_available",
                fallback_chain=[],
            )

        if prefer == "cost":
            candidates.sort(key=lambda m: (m.priority, m.cost_per_1k_prompt))
        elif prefer == "latency":
            candidates.sort(key=lambda m: (m.priority, m.avg_latency_ms))
        else:
            candidates.sort(key=lambda m: (
                m.priority,
                -len(set(m.capabilities) & set(caps)),
            ))

        primary = candidates[0]
        fallback_chain = [m.name for m in candidates[1:1 + max_fallback]]

        return RouteDecision(
            model_name=primary.name,
            provider=primary.provider,
            estimated_cost=primary.cost_per_1k_prompt * 1 + primary.cost_per_1k_completion * 1,
            estimated_latency_ms=primary.avg_latency_ms,
            reason=f"selected_by_{prefer}",
            fallback_chain=fallback_chain,
        )

    def record_failure(self, model_name: str) -> None:
        with self._lock:
            self._failure_counts[model_name] += 1

    def record_success(self, model_name: str) -> None:
        with self._lock:
            self._failure_counts[model_name] = max(0, self._failure_counts[model_name] - 1)

    def get_next_fallback(self, current_model: str,
                          task_type: str = "chat",
                          excluded: list[str] | None = None) -> str:
        """Get the next fallback model in the chain."""
        excluded = excluded or [current_model]
        decision = self.route(
            task_type=task_type,
            excluded_models=excluded,
        )
        return decision.model_name

    def stats(self) -> dict:
        with self._lock:
            return {
                "failure_counts": dict(self._failure_counts),
                "available_models": len(self.registry.list_models()),
            }


# ─────────────────────────────────────────
# Rate Limiter (Token Bucket)
# ─────────────────────────────────────────

class RateLimiter:
    """Token-bucket rate limiter for model API calls.

    Each model has its own bucket with configurable:
    - Tokens per interval (rate)
    - Bucket capacity (burst allowance)
    - Refill interval
    """

    def __init__(self) -> None:
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = threading.Lock()

    def configure(self, model_name: str, rate: float = 10.0,
                  capacity: int = 20, interval_sec: float = 1.0) -> None:
        with self._lock:
            self._buckets[model_name] = _TokenBucket(
                rate=rate, capacity=capacity, interval_sec=interval_sec,
            )

    def try_acquire(self, model_name: str, tokens: int = 1) -> bool:
        """Try to acquire tokens from the bucket. Returns True if allowed."""
        with self._lock:
            bucket = self._buckets.get(model_name)
            if bucket is None:
                bucket = _TokenBucket()
                self._buckets[model_name] = bucket
            return bucket.try_consume(tokens)

    def get_available(self, model_name: str) -> float:
        with self._lock:
            bucket = self._buckets.get(model_name)
            if bucket is None:
                return 0.0
            bucket._refill()
            return bucket._tokens

    def reset(self, model_name: str = "") -> None:
        with self._lock:
            if model_name:
                self._buckets.pop(model_name, None)
            else:
                self._buckets.clear()


class _TokenBucket:
    """Internal token bucket implementation."""

    def __init__(self, rate: float = 10.0,
                 capacity: int = 20, interval_sec: float = 1.0) -> None:
        self.rate = rate
        self.capacity = float(capacity)
        self.interval_sec = interval_sec
        self._tokens = float(capacity)
        self._last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(
            self.capacity,
            self._tokens + elapsed * self.rate / self.interval_sec,
        )
        self._last_refill = now

    def try_consume(self, tokens: int) -> bool:
        self._refill()
        if self._tokens >= tokens:
            self._tokens -= tokens
            return True
        return False


# ─────────────────────────────────────────
# Cost Tracker
# ─────────────────────────────────────────

@dataclass
class CostRecord:
    """Record of a single model call cost."""
    model_name: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    cost: float
    timestamp: str
    task_type: str = ""


class CostTracker:
    """Tracks token usage and cost per model call."""

    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry
        self._records: list[CostRecord] = []
        self._lock = threading.Lock()

    def record(self, model_name: str, prompt_tokens: int,
               completion_tokens: int, task_type: str = "") -> float:
        model = self.registry.get(model_name)
        cost = model.estimate_cost(prompt_tokens, completion_tokens) if model else 0.0

        record = CostRecord(
            model_name=model_name,
            provider=model.provider if model else "unknown",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost,
            timestamp=datetime.now(timezone.utc).isoformat(),
            task_type=task_type,
        )
        with self._lock:
            self._records.append(record)
        return cost

    def total_cost(self, model_name: str = "",
                   provider: str = "",
                   since: str = "") -> dict:
        with self._lock:
            records = self._records
            if model_name:
                records = [r for r in records if r.model_name == model_name]
            if provider:
                records = [r for r in records if r.provider == provider]
            if since:
                records = [r for r in records if r.timestamp >= since]

            total = sum(r.cost for r in records)
            total_prompt = sum(r.prompt_tokens for r in records)
            total_completion = sum(r.completion_tokens for r in records)

            return {
                "total_cost": round(total, 6),
                "total_prompt_tokens": total_prompt,
                "total_completion_tokens": total_completion,
                "total_calls": len(records),
                "records": [{
                    "model": r.model_name,
                    "provider": r.provider,
                    "prompt_tokens": r.prompt_tokens,
                    "completion_tokens": r.completion_tokens,
                    "cost": r.cost,
                    "timestamp": r.timestamp,
                    "task_type": r.task_type,
                } for r in records],
            }

    def summary_by_model(self) -> list[dict]:
        with self._lock:
            groups: dict[str, list[CostRecord]] = defaultdict(list)
            for r in self._records:
                groups[r.model_name].append(r)

            result = []
            for name, records in groups.items():
                result.append({
                    "model_name": name,
                    "calls": len(records),
                    "total_cost": round(sum(r.cost for r in records), 6),
                    "total_tokens": sum(r.prompt_tokens + r.completion_tokens for r in records),
                })
            return sorted(result, key=lambda x: x["total_cost"], reverse=True)

    def clear(self) -> None:
        with self._lock:
            self._records.clear()


# ─────────────────────────────────────────
# Orchestrator: Router + RateLimiter + CostTracker
# ─────────────────────────────────────────

class ModelOrchestrator:
    """Combines routing, rate limiting, and cost tracking into one interface.

    Typical usage:
        orch = ModelOrchestrator()
        model_name = orch.select_model("code", prefer="cost")
        if orch.limiter.try_acquire(model_name):
            # call model API ...
            orch.tracker.record(model_name, prompt_tokens, completion_tokens)
    """

    def __init__(self) -> None:
        self.registry = ModelRegistry()
        self.router = Router(self.registry)
        self.limiter = RateLimiter()
        self.tracker = CostTracker(self.registry)

        for model in self.registry.list_models():
            self.limiter.configure(
                model.name,
                rate=30.0 if model.provider == "local" else 10.0,
                capacity=60 if model.provider == "local" else 20,
            )

    def select_model(self, task_type: str = "chat",
                     prefer: str = "cost",
                     required_capabilities: list[str] | None = None,
                     max_fallback: int = 2) -> RouteDecision:
        """Select the best model and return full routing decision."""
        return self.router.route(
            task_type=task_type,
            prefer=prefer,
            required_capabilities=required_capabilities,
            max_fallback=max_fallback,
        )

    def try_call(self, task_type: str, prefer: str = "cost",
                 required_capabilities: list[str] | None = None,
                 attempt: int = 0,
                 excluded: list[str] | None = None) -> str | None:
        """Try to select a model that passes rate limiting.

        Returns model name or None if all options are exhausted.
        """
        excluded = excluded or []
        decision = self.router.route(
            task_type=task_type, prefer=prefer,
            required_capabilities=required_capabilities,
            excluded_models=excluded,
        )

        if not decision.model_name:
            return None

        if self.limiter.try_acquire(decision.model_name):
            return decision.model_name

        if decision.fallback_chain:
            for fb in decision.fallback_chain:
                if self.limiter.try_acquire(fb):
                    return fb

        return None

    def record_call_cost(self, model_name: str, prompt_tokens: int,
                         completion_tokens: int, task_type: str = "",
                         success: bool = True) -> float:
        if success:
            self.router.record_success(model_name)
        else:
            self.router.record_failure(model_name)
        return self.tracker.record(
            model_name, prompt_tokens, completion_tokens, task_type,
        )

    def snapshot(self) -> dict:
        return {
            "router": self.router.stats(),
            "costs": self.tracker.total_cost(),
        }


__all__ = [
    "ModelInfo", "ModelRegistry", "RouteDecision", "Router",
    "RateLimiter", "CostTracker", "CostRecord", "ModelOrchestrator",
]
