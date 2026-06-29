from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas import ExecutionTrace


@dataclass(frozen=True)
class TraceAuditResult:
    success: bool
    score: float
    failure_reason: str = ''
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)


def _step_name(event: dict[str, Any]) -> str:
    step = event.get('step')
    if isinstance(step, dict):
        return str(step.get('name') or step.get('id') or 'unknown_step')
    return 'unknown_step'


def _tool_name(event: dict[str, Any]) -> str:
    result = event.get('result')
    if isinstance(result, dict) and result.get('tool'):
        return str(result.get('tool'))
    step = event.get('step')
    if isinstance(step, dict):
        return str(step.get('tool') or 'unknown_tool')
    return 'unknown_tool'


def _result_status(event: dict[str, Any]) -> str:
    result = event.get('result')
    if isinstance(result, dict):
        return str(result.get('status') or 'unknown')
    return 'missing'


def audit_trace(trace: ExecutionTrace) -> TraceAuditResult:
    issues: list[str] = []
    recommendations: list[str] = []
    events = trace.events or []
    statuses = [_result_status(event) for event in events]
    tools = [_tool_name(event) for event in events]
    steps = [_step_name(event) for event in events]

    blocked_count = sum(1 for status in statuses if status == 'blocked')
    error_count = sum(1 for status in statuses if status == 'error')
    missing_result_count = sum(1 for status in statuses if status == 'missing')
    unknown_status_count = sum(1 for status in statuses if status == 'unknown')

    if not events:
        issues.append('no_trace_events')
        recommendations.append('record at least one execution event before evaluating the trace')
    if blocked_count:
        issues.append('blocked_tool_result')
        recommendations.append('inspect tool guard reasons before retrying blocked actions')
    if error_count:
        issues.append('tool_error_result')
        recommendations.append('inspect failing tool payloads and add targeted recovery checks')
    if missing_result_count:
        issues.append('missing_tool_result')
        recommendations.append('store every step result in the trace event')
    if unknown_status_count:
        issues.append('unknown_tool_status')
        recommendations.append('normalize tool result status values')
    if trace.success is False and not (blocked_count or error_count):
        issues.append('trace_marked_failed_without_error_status')
        recommendations.append('align trace.success with event-level tool statuses')

    score = 1.0
    if not events:
        score -= 0.40
    score -= min(blocked_count * 0.25, 0.50)
    score -= min(error_count * 0.30, 0.60)
    score -= min(missing_result_count * 0.20, 0.40)
    score -= min(unknown_status_count * 0.10, 0.30)
    if trace.success is False:
        score -= 0.20
    score = round(max(0.0, min(1.0, score)), 3)

    success = bool(trace.success) and score >= 0.70 and not any(
        issue in issues for issue in ['blocked_tool_result', 'tool_error_result', 'missing_tool_result']
    )

    failure_reason = ''
    if not success:
        if blocked_count:
            failure_reason = 'blocked tool result'
        elif error_count:
            failure_reason = 'tool error result'
        elif missing_result_count:
            failure_reason = 'missing tool result'
        elif not events:
            failure_reason = 'no trace events'
        else:
            failure_reason = 'execution trace did not pass audit'

    if success and not recommendations:
        recommendations.append('preserve complete trace events as evidence for future lessons')

    evidence = {
        'trace_id': trace.id,
        'task_id': trace.task_id,
        'event_count': len(events),
        'tools': sorted(set(tools)),
        'steps': steps,
        'statuses': statuses,
        'blocked_count': blocked_count,
        'error_count': error_count,
        'missing_result_count': missing_result_count,
        'trace_result_status': trace.result.get('status') if isinstance(trace.result, dict) else None,
    }

    return TraceAuditResult(
        success=success,
        score=score,
        failure_reason=failure_reason,
        issues=issues,
        recommendations=recommendations,
        evidence=evidence,
    )
