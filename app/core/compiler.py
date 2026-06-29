from app.schemas import ContextPack, TaskPack


def compile_task(context: ContextPack) -> TaskPack:
    goal = context.query[:300] if context.query else "Process context"
    return TaskPack(
        goal=goal,
        steps=[
            {"id": 1, "name": "analyze_context", "type": "reasoning", "tool": "echo"},
            {"id": 2, "name": "plan_next_action", "type": "planning", "tool": "echo"},
            {"id": 3, "name": "produce_result", "type": "output", "tool": "echo"},
        ],
        constraints=["log every step", "do not execute high-risk actions without review"],
        tools=["echo"],
        risk_level="low",
        success_criteria=["pipeline completes", "trace is written"],
    )
