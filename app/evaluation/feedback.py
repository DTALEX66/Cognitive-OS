from app.schemas import EvalResult, ExecutionTrace, MachineLesson
from app.evaluation.lesson_engine import lesson_from_eval


def compile_lesson(eval_result: EvalResult, trace: ExecutionTrace) -> MachineLesson:
    return lesson_from_eval(eval_result, trace)
