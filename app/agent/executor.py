from app.schemas import ExecutionTrace, TaskPack
from app.tools.registry import run_tool


def execute(task: TaskPack) -> ExecutionTrace:
    trace = ExecutionTrace(task_id=task.id)
    results = []
    success = True
    for step in task.steps:
        result = run_tool(
            step.get("tool", "echo"),
            step,
            dry_run=step.get("dry_run"),
        )
        event = {"step": step, "result": result}
        trace.events.append(event)
        results.append(result)
        if result.get("status") in {"error", "blocked"}:
            success = False
    trace.result = {"status": "done" if success else "completed_with_errors", "outputs": results}
    trace.success = success
    return trace
