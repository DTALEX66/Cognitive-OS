"""Policy Engine — 学习策略引擎（CC 权限模型 + hooks 适配）

从 CC 权限系统和 hooks 系统提取的规则引擎：
  - PermissionMode → 学习模式
  - 权限链 → 规则校验链
  - hooks Pre/Post → 学习前/后处理
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from enum import Enum


class LearningMode(str, Enum):
    FOCUS = "focus"           # CC: bypassPermissions — 专注模式
    REVIEW = "review"         # CC: default — 复习模式
    EXAM = "exam"             # CC: plan — 考试模式


class PolicyEngine:
    """学习策略引擎"""

    def __init__(self, store: Any) -> None:
        self._store = store
        self._mode = LearningMode.REVIEW
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []

    def set_mode(self, mode: LearningMode) -> None:
        self._mode = mode

    # CC: 权限链 → 规则校验
    def check_action(self, action: str, context: dict) -> dict:
        """检查学习动作是否被允许（类比 CC canUseTool）"""
        if self._mode == LearningMode.FOCUS:
            return {"allowed": True}  # 专注模式，全部放行
        if action == "skip" and self._mode == LearningMode.EXAM:
            return {"allowed": False, "reason": "exam mode: cannot skip"}
        if action == "peek_answer" and context.get("attempts", 0) < 3:
            return {"allowed": False, "reason": "must attempt 3 times first"}
        return {"allowed": True}

    # CC: executePreToolHooks
    def register_pre_hook(self, hook: Callable) -> None:
        self._pre_hooks.append(hook)

    # CC: executePostToolHooks
    def register_post_hook(self, hook: Callable) -> None:
        self._post_hooks.append(hook)

    def run_pre_hooks(self, action: str) -> list:
        return [h(action) for h in self._pre_hooks]

    def run_post_hooks(self, action: str, result: Any) -> list:
        return [h(action, result) for h in self._post_hooks]

class LearningPolicy:
    def __init__(self, store=None):
        self.store = store
    def next_actions(self, count=5):
        if not self.store:
            return []
        try:
            rows = self.store.conn.execute(
                "SELECT id, title, memory_strength FROM cards ORDER BY memory_strength ASC LIMIT ?",
                (count,)).fetchall()
            return [{"id": r[0], "title": r[1], "memory_strength": r[2]} for r in rows]
        except:
            return []
def next_action_score(due_priority=0.5, weakness_priority=0.5):
    return round((due_priority * 0.5 + weakness_priority * 0.5), 3)
