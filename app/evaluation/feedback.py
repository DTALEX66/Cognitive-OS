from app.schemas import EvalResult, ExecutionTrace, MachineLesson


def compile_lesson(eval_result: EvalResult, trace: ExecutionTrace) -> MachineLesson:
    lesson_type = "success" if eval_result.success else "failure"
    pattern = "pipeline completed" if eval_result.success else "pipeline failed"
    future_constraint = eval_result.improvement or "inspect trace before the next run"
    return MachineLesson(
        pattern=pattern,
        lesson_type=lesson_type,
        future_constraint=future_constraint,
        evidence_trace_id=trace.id,
    )
