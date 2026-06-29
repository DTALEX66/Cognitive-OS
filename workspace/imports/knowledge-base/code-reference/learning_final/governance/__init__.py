"""Governance Engine — 学习治理系统（CC 权限模型适配）

从 CC 权限系统提取的治理模式：
  - PermissionMode → 学习模式
  - 强制权限链 → 规则链（Zod→自检→Hook→执行）
  - PolicyEngine → 策略引擎
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from enum import Enum


class StudyMode(str, Enum):
    FOCUS = "focus"         # CC: bypassPermissions — 全放行
    STANDARD = "standard"   # CC: default — 标准交互确认
    DISCIPLINE = "discipline"  # CC: plan — 严格规则


class GovernanceEngine:
    """学习治理引擎 — 规则链"""

    def __init__(self, store: Any) -> None:
        self._store = store
        self._mode = StudyMode.STANDARD

    # setPermissionMode
    def set_mode(self, mode: StudyMode) -> None:
        self._mode = mode

    # CC: 强制权限链（Zod→自检→pre-hooks→canUseTool→执行→post-hooks）
    def check(self, action: str, context: dict) -> dict:
        """治理检查链"""
        chain = [
            ("schema_validate", self._schema_validate),
            ("self_check", self._self_check),
            ("mode_check", self._mode_check),
            ("quota_check", self._quota_check),
        ]
        results = []
        for name, fn in chain:
            result = fn(action, context)
            results.append({name: result})
            if not result["allowed"]:
                return {"allowed": False, "chain": results}
        return {"allowed": True, "chain": results}

    def _schema_validate(self, action: str, ctx: dict) -> dict:
        if action not in ["study", "review", "exam", "skip", "peek"]:
            return {"allowed": False, "reason": f"unknown action: {action}"}
        return {"allowed": True}

    def _self_check(self, action: str, ctx: dict) -> dict:
        if self._mode == StudyMode.DISCIPLINE and action in ["skip", "peek"]:
            return {"allowed": False, "reason": "discipline mode: no skipping"}
        return {"allowed": True}

    def _mode_check(self, action: str, ctx: dict) -> dict:
        if self._mode == StudyMode.FOCUS:
            return {"allowed": True}
        if action == "skip" and ctx.get("attempts", 0) < 2:
            return {"allowed": False, "reason": "must attempt at least 2 times"}
        return {"allowed": True}

    def _quota_check(self, action: str, ctx: dict) -> dict:
        today = datetime.now(timezone.utc).isoformat()[:10]
        count = self._store.conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE created_at >= ?", (today,)).fetchone()[0]
        if count > 100:
            return {"allowed": False, "reason": "daily review quota exceeded (100)"}
        return {"allowed": True}
