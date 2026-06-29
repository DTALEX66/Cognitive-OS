from app.schemas import ExecutionTrace, EvalResult
from app.evaluation.trace_audit import audit_trace


def evaluate(trace: ExecutionTrace) -> EvalResult:
    audit = audit_trace(trace)
    improvement = '; '.join(audit.recommendations)
    return EvalResult(
        success=audit.success,
        score=audit.score,
        failure_reason=audit.failure_reason,
        improvement=improvement,
        issues=audit.issues,
        recommendations=audit.recommendations,
        audit=audit.evidence,
    )
