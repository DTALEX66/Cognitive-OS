from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

from app.schemas import LearningCard, ReviewEvent

SCORE_BREAKPOINTS = (0.3, 0.6, 0.9)
DAY_SECONDS = 86_400


def score_to_grade(score: float) -> int:
    if score < SCORE_BREAKPOINTS[0]:
        return 1
    if score < SCORE_BREAKPOINTS[1]:
        return 2
    if score < SCORE_BREAKPOINTS[2]:
        return 3
    return 4


def parse_iso(value: str | None, fallback: datetime | None = None) -> datetime:
    if not value:
        return fallback or datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return fallback or datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def retrievability(card: LearningCard, now: datetime | None = None) -> float:
    now_dt = now or datetime.now(timezone.utc)
    last_review = parse_iso(card.last_review_at or card.created_at, fallback=now_dt)
    elapsed_days = max((now_dt - last_review).total_seconds() / DAY_SECONDS, 0.0)
    stability = max(card.stability, 0.1)
    return round(math.exp(math.log(0.9) * elapsed_days / stability), 4)


def _next_difficulty(difficulty: float, grade: int) -> float:
    delta = {1: 0.8, 2: 0.35, 3: -0.15, 4: -0.45}[grade]
    return round(max(1.0, min(10.0, difficulty + delta)), 2)


def _next_stability(card: LearningCard, grade: int, current_retrievability: float) -> float:
    stability = max(card.stability, 0.1)
    difficulty_factor = max(0.25, (11.0 - card.difficulty) / 10.0)

    if grade == 1:
        return round(max(0.25, stability * 0.45), 2)
    if grade == 2:
        growth = 1.15 * difficulty_factor
    elif grade == 3:
        growth = 1.80 * difficulty_factor
    else:
        growth = 2.50 * difficulty_factor

    recall_bonus = max(0.4, 1.15 - current_retrievability)
    return round(min(36500.0, stability + growth * recall_bonus), 2)


def _interval_for_grade(stability: float, grade: int) -> int:
    if grade == 1:
        return DAY_SECONDS
    multiplier = {2: 0.8, 3: 1.4, 4: 2.2}[grade]
    days = max(1.0, stability * multiplier)
    return int(days * DAY_SECONDS)


def review_card(card: LearningCard, score: float, now: datetime | None = None) -> tuple[LearningCard, ReviewEvent]:
    now_dt = now or datetime.now(timezone.utc)
    bounded_score = max(0.0, min(float(score), 1.0))
    grade = score_to_grade(bounded_score)
    current_retrievability = retrievability(card, now=now_dt)
    previous_interval = card.interval_seconds
    next_difficulty = _next_difficulty(card.difficulty, grade)
    stability_input = card.model_copy(update={'difficulty': next_difficulty})
    next_stability = _next_stability(stability_input, grade, current_retrievability)
    next_interval = _interval_for_grade(next_stability, grade)
    next_review = now_dt + timedelta(seconds=next_interval)

    updated = card.model_copy(
        update={
            'difficulty': next_difficulty,
            'stability': next_stability,
            'interval_seconds': next_interval,
            'next_review_at': next_review.isoformat(),
            'last_review_at': now_dt.isoformat(),
            'review_count': card.review_count + 1,
            'lapses': card.lapses + (1 if grade == 1 else 0),
        }
    )
    event = ReviewEvent(
        card_id=card.id,
        score=bounded_score,
        grade=grade,
        retrievability=current_retrievability,
        previous_interval_seconds=previous_interval,
        next_interval_seconds=next_interval,
        created_at=now_dt.isoformat(),
    )
    return updated, event
