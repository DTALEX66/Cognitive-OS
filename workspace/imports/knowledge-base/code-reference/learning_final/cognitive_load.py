"""Cognitive Load Engine — 认知负荷管理系统（hooks 适配）

从 hooks 系统的 Pre/Post 生命周期提取的负荷管理
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum
import json


class LoadLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    OVERLOAD = "overload"


LOAD_THRESHOLDS = {
    "cards_per_session": {"low": 15, "moderate": 30, "high": 50},
    "time_per_session_min": {"low": 20, "moderate": 45, "high": 90},
}


class CognitiveLoadEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def estimate(self, session_plan: dict) -> LoadLevel:
        cards = session_plan.get("cards", 0)
        minutes = session_plan.get("minutes", 0)
        if cards <= LOAD_THRESHOLDS["cards_per_session"]["low"] and minutes <= LOAD_THRESHOLDS["time_per_session_min"]["low"]:
            return LoadLevel.LOW
        if cards <= LOAD_THRESHOLDS["cards_per_session"]["moderate"] and minutes <= LOAD_THRESHOLDS["time_per_session_min"]["moderate"]:
            return LoadLevel.MODERATE
        if cards <= LOAD_THRESHOLDS["cards_per_session"]["high"] and minutes <= LOAD_THRESHOLDS["time_per_session_min"]["high"]:
            return LoadLevel.HIGH
        return LoadLevel.OVERLOAD

    def suggest_break(self, session_history: list[dict]) -> Optional[dict]:
        recent = session_history[-10:] if len(session_history) >= 10 else session_history
        if len(recent) >= 5:
            avg_rating = sum(r.get("rating", 3) for r in recent) / len(recent)
            if avg_rating < 2.5:
                return {"suggestion": "take a break", "reason": "declining accuracy"}
        return None

    def optimal_session(self, available_minutes: int) -> dict:
        max_cards = min(int(available_minutes / 2), 25)
        return {
            "recommended_cards": max_cards,
            "recommended_minutes": min(available_minutes, 60),
            "load": self.estimate({"cards": max_cards, "minutes": min(available_minutes, 60)}).value,
        }

    def evaluate(self, params: dict) -> dict:
        new_concepts = params.get("new_concepts", 0.5)
        abstraction = params.get("abstraction", 0.5)
        load_score = cognitive_load_score(new_concepts, abstraction)
        if load_score < 0.3:
            level = "low"
        elif load_score < 0.6:
            level = "moderate"
        elif load_score < 0.8:
            level = "high"
        else:
            level = "overload"
        result = {"load_score": load_score, "level": level}
        if self._store:
            try:
                ts = datetime.now(timezone.utc).isoformat()
                self._store.conn.execute(
                    "INSERT INTO diagnostics (target_type, target_id, diag_type, details, created_at) VALUES (?,?,?,?,?)",
                    ("session", 0, "cognitive_load", json.dumps(result), ts))
                self._store.conn.commit()
            except:
                pass
        self._last_result = result
        return result

    def latest(self):
        return getattr(self, "_last_result", None)

    def history(self, limit: int = 20):
        if self._store:
            try:
                rows = self._store.conn.execute(
                    "SELECT details FROM diagnostics WHERE diag_type=? ORDER BY created_at DESC LIMIT ?",
                    ("cognitive_load", limit)).fetchall()
                return [json.loads(r[0]) for r in rows]
            except:
                pass
        return []



def cognitive_load_score(new_concept_count_score=0.5, abstraction_score=0.5):
    return round((new_concept_count_score * 0.6 + abstraction_score * 0.4), 3)
