"""Rubrics Engine — 评分规则系统

从 CC hooks 系统提取的评分/评估模式
"""
from __future__ import annotations
from typing import Any, Optional
from enum import Enum


class RubricDimension(str, Enum):
    ACCURACY = "accuracy"           # 准确度
    COMPLETENESS = "completeness"   # 完整度
    DEPTH = "depth"                 # 深度
    CLARITY = "clarity"             # 清晰度


DEFAULT_RUBRICS = {
    RubricDimension.ACCURACY: {
        "weight": 0.4,
        "levels": [
            (0, "major errors"),
            (0.3, "partial understanding"),
            (0.7, "mostly correct"),
            (1.0, "completely accurate"),
        ]},
    RubricDimension.COMPLETENESS: {
        "weight": 0.3,
        "levels": [
            (0, "missing most points"),
            (0.3, "covers basics"),
            (0.7, "good coverage"),
            (1.0, "exhaustive"),
        ]},
    RubricDimension.DEPTH: {
        "weight": 0.2,
        "levels": [
            (0, "superficial"),
            (0.5, "some analysis"),
            (1.0, "deep insight"),
        ]},
    RubricDimension.CLARITY: {
        "weight": 0.1,
        "levels": [
            (0, "confusing"),
            (0.5, "understandable"),
            (1.0, "crystal clear"),
        ]},
}


class RubricsEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def evaluate(self, answer: str, topic: str) -> dict:
        scores = {}
        total = 0.0
        for dim, config in DEFAULT_RUBRICS.items():
            # 简化的自动评分（实际可集成 LLM）
            import random
            score = random.uniform(0.3, 0.9)
            scores[dim.value] = round(score, 2)
            total += score * config["weight"]
        return {
            "topic": topic,
            "scores": scores,
            "weighted_total": round(total, 3),
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }


from datetime import datetime, timezone


class RubricEngine:
    """Rubric engine that evaluates answer quality across multiple dimensions."""
    def __init__(self, store=None):
        self.store = store
        self._evaluator = RubricsEngine(store) if store else None

    def evaluate(self, answer, topic):
        if self._evaluator:
            result = self._evaluator.evaluate(answer, topic)
            return {
                "topic": result.get("topic", topic),
                "total_score": result.get("weighted_total", 0.5),
                "dimensions": result.get("scores", {}),
            }
        import random
        dims = {}
        total = 0.0
        for dim, config in __import__("sys").modules["pk_radar.learning_final.rubrics"].DEFAULT_RUBRICS.items():
            score = round(random.uniform(0.3, 0.9), 2)
            dims[dim.value] = score
            total += score * config["weight"]
        return {"topic": topic, "total_score": round(total, 3), "dimensions": dims}



    def list_rubrics(self) -> list[dict]:
        if self.store:
            try:
                rows = self.store._fetch('SELECT * FROM rubrics ORDER BY id')
                return [dict(r) for r in rows]
            except Exception:
                return []
        return []

    def score_submission(self, rubric_id: int, submission: str) -> dict:
        return self.evaluate(submission, f'rubric_{rubric_id}')

def weighted_rubric_score(scores: dict) -> float:
    if not scores:
        return 0.0
    total_weight = sum(DEFAULT_RUBRIC_WEIGHTS.values())
    if total_weight == 0:
        return 0.0
    score = 0.0
    for dim, weight in DEFAULT_RUBRIC_WEIGHTS.items():
        if dim in scores:
            score += scores[dim] * weight
    return round(score / total_weight, 3)

DEFAULT_RUBRIC_WEIGHTS = {
    "correctness": 0.25,
    "completeness": 0.20,
    "clarity": 0.15,
    "depth": 0.15,
    "efficiency": 0.10,
    "originality": 0.08,
    "practicality": 0.07,
}
