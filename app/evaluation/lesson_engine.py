from __future__ import annotations

from app.schemas import EvalResult, ExecutionTrace, MachineLesson


def _tools_text(eval_result: EvalResult) -> str:
    tools = eval_result.audit.get('tools', [])
    if isinstance(tools, list) and tools:
        return ', '.join(str(tool) for tool in tools[:5])
    return 'unknown tools'


def _event_count(eval_result: EvalResult) -> int:
    value = eval_result.audit.get('event_count', 0)
    return int(value) if isinstance(value, int) else 0


def lesson_from_eval(eval_result: EvalResult, trace: ExecutionTrace) -> MachineLesson:
    tools = _tools_text(eval_result)
    event_count = _event_count(eval_result)

    if eval_result.success:
        return MachineLesson(
            pattern=f'successful pipeline with {event_count} trace events using {tools}',
            lesson_type='success',
            future_constraint='Preserve complete trace evidence and keep deterministic audit checks in the next run.',
            evidence_trace_id=trace.id,
        )

    issues = set(eval_result.issues)
    if 'blocked_tool_result' in issues:
        return MachineLesson(
            pattern=f'blocked tool execution detected in {tools}',
            lesson_type='constraint',
            future_constraint='Inspect guard reasons and require explicit review before retrying blocked tool actions.',
            evidence_trace_id=trace.id,
        )

    if 'tool_error_result' in issues:
        return MachineLesson(
            pattern=f'tool error during execution in {tools}',
            lesson_type='failure',
            future_constraint='Add a targeted recovery check for the failing tool payload before rerun.',
            evidence_trace_id=trace.id,
        )

    if 'missing_tool_result' in issues or 'no_trace_events' in issues:
        return MachineLesson(
            pattern='execution trace lacked sufficient evidence',
            lesson_type='anti_pattern',
            future_constraint='Record every step result before evaluating or saving machine lessons.',
            evidence_trace_id=trace.id,
        )

    return MachineLesson(
        pattern=f'audited pipeline failure: {eval_result.failure_reason or "unknown failure"}',
        lesson_type='failure',
        future_constraint=eval_result.improvement or 'Inspect trace audit issues before the next run.',
        evidence_trace_id=trace.id,
    )
