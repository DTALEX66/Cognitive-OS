"""Rubrics Engine — 评分规则系统

Evaluates explain-back answers across multiple quality dimensions
with configurable weights and level descriptions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Literal


class RubricDimension(str, Enum):
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    DEPTH = "depth"
    CLARITY = "clarity"


DEFAULT_RUBRICS: dict[RubricDimension, dict] = {
    RubricDimension.ACCURACY: {
        "weight": 0.35,
        "levels": [
            (0.0, "major errors — key facts are wrong"),
            (0.35, "partial understanding — some correct facts, several errors"),
            (0.7, "mostly correct — minor inaccuracies"),
            (1.0, "completely accurate — no errors"),
        ],
    },
    RubricDimension.COMPLETENESS: {
        "weight": 0.30,
        "levels": [
            (0.0, "missing most key points"),
            (0.35, "covers basics but skips important details"),
            (0.7, "good coverage — most key points present"),
            (1.0, "exhaustive — all key points covered"),
        ],
    },
    RubricDimension.DEPTH: {
        "weight": 0.20,
        "levels": [
            (0.0, "superficial — no explanation of why or how"),
            (0.35, "some analysis — touches on mechanisms"),
            (0.7, "solid depth — explains mechanisms and reasoning"),
            (1.0, "deep insight — connects to broader context"),
        ],
    },
    RubricDimension.CLARITY: {
        "weight": 0.15,
        "levels": [
            (0.0, "confusing — hard to follow"),
            (0.35, "understandable with effort"),
            (0.7, "clear — easy to follow"),
            (1.0, "crystal clear — intuitive and well-structured"),
        ],
    },
}


def _closest_level(levels: list[tuple[float, str]], raw: float) -> tuple[float, str]:
    """Find the nearest level description for a raw score."""
    best = levels[0]
    for score, desc in levels:
        if abs(raw - score) < abs(raw - best[0]):
            best = (score, desc)
    return best


@dataclass
class RubricResult:
    topic: str
    dimension_scores: dict[str, float] = field(default_factory=dict)
    dimension_feedback: dict[str, str] = field(default_factory=dict)
    weighted_total: float = 0.0
    gaps: list[str] = field(default_factory=list)
    evaluated_at: str = ""


def _detect_gaps(text: str) -> list[str]:
    """Rule-based gap detection for teach-back explanations."""
    gaps: list[str] = []
    if len(text) < 80:
        gaps.append("explanation too brief to demonstrate understanding")
    if "?" not in text and "why" not in text.lower() and "because" not in text.lower():
        gaps.append("missing reasoning — no causal explanation provided")
    if "example" not in text.lower() and "like " not in text.lower() and "for instance" not in text.lower():
        gaps.append("lacks concrete examples or analogies")
    return gaps


def _guess_dimension_scores(text: str) -> dict[str, float]:
    """Heuristic scoring per dimension based on explanation text features.

    This is a deterministic fallback. In production the system can
    delegate to an LLM judge for richer evaluation.
    """
    word_count = len(text.split())
    has_structure = any(m in text for m in ["首先", "其次", "最后", "第一", "第二", "一是", "二是", "step", "first", "second", "finally"])
    has_examples = any(p in text.lower() for p in ["example", "for instance", "like ", "such as", "e.g."])
    has_causality = any(p in text.lower() for p in ["because", "therefore", "so that", "due to", "导致", "因为", "所以"])
    has_analogy = any(p in text.lower() for p in ["类比", "类似", "analogy", "similar to", "就像"])

    # Accuracy: heuristic based on length + structure (longer, structured = more likely correct)
    accuracy = min(1.0, 0.3 + word_count / 500 * 0.5 + (0.15 if has_structure else 0))

    # Completeness: length + structure
    completeness = min(1.0, 0.2 + word_count / 300 * 0.4 + (0.2 if has_structure else 0) + (0.1 if has_examples else 0))

    # Depth: causality + analogy + length
    depth = 0.2 + (0.3 if has_causality else 0) + (0.2 if has_analogy else 0)
    depth = min(1.0, depth + word_count / 800 * 0.3)

    # Clarity: structure + examples
    clarity = 0.4 + (0.3 if has_structure else 0) + (0.15 if has_examples else 0)
    clarity = min(1.0, clarity + word_count / 400 * 0.15)

    return {
        "accuracy": round(accuracy, 2),
        "completeness": round(completeness, 2),
        "depth": round(depth, 2),
        "clarity": round(clarity, 2),
    }


def evaluate(text: str, topic: str) -> RubricResult:
    """Score an explanation against the default rubric."""
    now = datetime.now(timezone.utc).isoformat()
    dim_scores = _guess_dimension_scores(text)
    dim_feedback: dict[str, str] = {}
    total = 0.0

    for dim, config in DEFAULT_RUBRICS.items():
        raw = dim_scores.get(dim.value, 0.5)
        level_score, level_desc = _closest_level(config["levels"], raw)
        dim_feedback[dim.value] = level_desc
        dim_scores[dim.value] = round(level_score, 2)
        total += level_score * config["weight"]

    gaps = _detect_gaps(text)

    return RubricResult(
        topic=topic,
        dimension_scores=dim_scores,
        dimension_feedback=dim_feedback,
        weighted_total=round(total, 3),
        gaps=gaps,
        evaluated_at=now,
    )


def weighted_total(dimension_scores: dict[str, float]) -> float:
    """Compute weighted total from raw dimension scores."""
    total = 0.0
    for dim, config in DEFAULT_RUBRICS.items():
        score = dimension_scores.get(dim.value, 0.0)
        total += score * config["weight"]
    return round(total, 3)


def list_rubric_descriptions() -> list[dict]:
    """Return the rubric configuration for client-side display."""
    return [
        {
            "dimension": dim.value,
            "weight": config["weight"],
            "levels": [{"score": s, "description": d} for s, d in config["levels"]],
        }
        for dim, config in DEFAULT_RUBRICS.items()
    ]
