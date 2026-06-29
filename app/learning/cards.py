from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.learning.fsrs import parse_iso, review_card as fsrs_review_card
from app.schemas import CoreObject, LearningCard, ReviewEvent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CARD_PATH = PROJECT_ROOT / 'data' / 'memory' / 'learning_cards.jsonl'
REVIEW_PATH = PROJECT_ROOT / 'data' / 'memory' / 'review_events.jsonl'


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _append_jsonl(path: Path, payload: str) -> None:
    _ensure_parent(path)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(payload + '\n')


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def save_card(card: LearningCard) -> None:
    _append_jsonl(CARD_PATH, card.model_dump_json(ensure_ascii=False))


def save_review_event(event: ReviewEvent) -> None:
    _append_jsonl(REVIEW_PATH, event.model_dump_json(ensure_ascii=False))


def list_cards() -> list[LearningCard]:
    latest: dict[str, LearningCard] = {}
    order: list[str] = []
    for row in _read_jsonl(CARD_PATH):
        try:
            card = LearningCard(**row)
        except Exception:
            continue
        if card.id not in latest:
            order.append(card.id)
        latest[card.id] = card
    return [latest[card_id] for card_id in order if card_id in latest]


def list_review_events() -> list[ReviewEvent]:
    events = []
    for row in _read_jsonl(REVIEW_PATH):
        try:
            events.append(ReviewEvent(**row))
        except Exception:
            continue
    return events


def get_card(card_id: str) -> LearningCard | None:
    for card in list_cards():
        if card.id == card_id:
            return card
    return None


def create_card(
    front: str,
    back: str,
    *,
    source: str = 'manual',
    source_object_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> LearningCard:
    card = LearningCard(
        front=front.strip(),
        back=back.strip(),
        source=source,
        source_object_id=source_object_id,
        metadata=metadata or {},
    )
    save_card(card)
    return card


def create_card_from_document(doc: CoreObject, front: str | None = None, back: str | None = None) -> LearningCard:
    normalized = ' '.join((doc.content or '').split())
    derived_front = front or normalized[:120] or 'Review this document'
    derived_back = back or normalized
    return create_card(
        derived_front,
        derived_back,
        source=doc.source,
        source_object_id=doc.id,
        metadata={'route': doc.route, **doc.metadata},
    )


def review_learning_card(card_id: str, score: float, now: datetime | None = None) -> tuple[LearningCard, ReviewEvent]:
    card = get_card(card_id)
    if card is None:
        raise KeyError(f'card not found: {card_id}')
    updated, event = fsrs_review_card(card, score, now=now)
    save_card(updated)
    save_review_event(event)
    return updated, event


def due_cards(now: datetime | None = None) -> list[LearningCard]:
    now_dt = now or datetime.now(timezone.utc)
    due = []
    for card in list_cards():
        if parse_iso(card.next_review_at, fallback=now_dt) <= now_dt:
            due.append(card)
    return due
