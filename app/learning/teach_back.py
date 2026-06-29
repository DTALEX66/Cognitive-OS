"""Teach-Back Engine — Feynman technique for learning verification

Users explain a concept in their own words. The system evaluates the
explanation using the RubricEngine, identifies gaps/weak points, and
tracks progress over time.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.learning import rubrics
from app.schemas import TeachBackSession

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEACH_BACK_PATH = PROJECT_ROOT / 'data' / 'memory' / 'teach_back.jsonl'

AVAILABLE_METHODS = [
    "feynman",
    "analogy",
    "simplify",
    "code_demo",
    "visual_map",
]


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, payload: str) -> None:
    _ensure_parent(path)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(payload + '\n')


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def list_methods() -> list[str]:
    """Return available teach-back methods."""
    return list(AVAILABLE_METHODS)


def submit_explanation(
    card_id: str,
    explanation: str,
    method: str = "feynman",
) -> TeachBackSession:
    """Submit a teach-back explanation and auto-evaluate it.

    The explanation is scored immediately using the rubric engine.
    Gaps and dimension scores are computed and stored.
    """
    if method not in AVAILABLE_METHODS:
        method = "feynman"

    result = rubrics.evaluate(explanation, topic=card_id)

    session = TeachBackSession(
        card_id=card_id,
        method=method,
        explanation=explanation.strip(),
        total_score=result.weighted_total,
        dimension_scores=result.dimension_scores,
        gaps=result.gaps,
    )

    _append_jsonl(TEACH_BACK_PATH, session.model_dump_json(ensure_ascii=False))
    return session


def evaluate_session(session_id: str) -> dict[str, Any] | None:
    """Re-evaluate a stored teach-back session and update its scores."""
    sessions = list_sessions_raw()
    for s in sessions:
        if s.get("id") == session_id:
            result = rubrics.evaluate(
                s.get("explanation", ""),
                topic=s.get("card_id", ""),
            )
            now = datetime.now(timezone.utc).isoformat()
            s["total_score"] = result.weighted_total
            s["dimension_scores"] = result.dimension_scores
            s["gaps"] = result.gaps
            s["evaluated_at"] = now
            return {
                "session_id": session_id,
                "total_score": result.weighted_total,
                "dimension_scores": result.dimension_scores,
                "dimension_feedback": result.dimension_feedback,
                "gaps": result.gaps,
                "evaluated_at": now,
            }
    return None


def list_sessions(card_id: str | None = None) -> list[TeachBackSession]:
    """List teach-back sessions, optionally filtered by card_id."""
    raw = list_sessions_raw()
    if card_id:
        raw = [s for s in raw if s.get("card_id") == card_id]
    sessions: list[TeachBackSession] = []
    for row in raw:
        try:
            sessions.append(TeachBackSession(**row))
        except Exception:
            continue
    return sessions


def list_sessions_raw() -> list[dict[str, Any]]:
    """Read all teach-back sessions as raw dicts."""
    return _read_jsonl(TEACH_BACK_PATH)


def weak_points(card_id: str) -> dict[str, Any]:
    """Aggregate weak points across all teach-back sessions for a card.

    Returns a dict with:
    - total_sessions: count of sessions
    - average_score: mean total_score across sessions
    - recurring_gaps: gaps that appear in 50%+ sessions
    - all_gaps: union of all gaps found
    - dimension_averages: average per-dimension score
    """
    sessions = list_sessions(card_id)
    if not sessions:
        return {
            "card_id": card_id,
            "total_sessions": 0,
            "average_score": 0.0,
            "recurring_gaps": [],
            "all_gaps": [],
            "dimension_averages": {},
        }

    total = len(sessions)
    total_score_sum = sum(s.total_score for s in sessions)
    gap_counts: dict[str, int] = {}
    dim_sums: dict[str, float] = {}

    for s in sessions:
        for g in s.gaps:
            gap_counts[g] = gap_counts.get(g, 0) + 1
        for dim, score in s.dimension_scores.items():
            dim_sums[dim] = dim_sums.get(dim, 0.0) + score

    recurring: list[str] = [
        gap for gap, count in gap_counts.items()
        if count / total >= 0.5
    ]

    dim_avgs = {
        dim: round(total_sum / total, 3)
        for dim, total_sum in dim_sums.items()
    }

    return {
        "card_id": card_id,
        "total_sessions": total,
        "average_score": round(total_score_sum / total, 3),
        "recurring_gaps": sorted(recurring),
        "all_gaps": sorted(set(gap_counts.keys())),
        "dimension_averages": dict(sorted(dim_avgs.items())),
    }


def get_session(session_id: str) -> TeachBackSession | None:
    """Retrieve a single session by ID."""
    for s in list_sessions():
        if s.id == session_id:
            return s
    return None
