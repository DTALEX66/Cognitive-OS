"""A转B转译系统 — 判断人是否掌握 → 转机器知识"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json

TRANSLATION_THRESHOLD = 0.7

class AToBEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def find_candidates(self, min_strength: float = TRANSLATION_THRESHOLD,
                        min_reviews: int = 3) -> list[dict]:
        cur = self._store.conn.execute(
            "SELECT id, title, content, memory_strength, review_count, deck FROM cards WHERE memory_strength >= ? AND review_count >= ? ORDER BY memory_strength DESC",
            (min_strength, min_reviews))
        return [dict(r) for r in cur.fetchall()]

    def translate(self, card_id: int, b_title: str = "",
                  b_content: str = "", b_unit_type: str = "rule") -> int:
        card = self._store.conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        if not card:
            return -1
        ts = datetime.now(timezone.utc).isoformat()
        # Check existing candidate for this card
        existing = self._store.conn.execute(
            "SELECT id FROM a_to_b_candidates WHERE a_source_type='card' AND a_source_id=?", (card_id,)).fetchone()
        if existing:
            self._store.conn.execute(
                "UPDATE a_to_b_candidates SET b_title=?, b_content=?, b_unit_type=?, updated_at=? WHERE id=?",
                (b_title or card["title"], b_content or card["content"], b_unit_type, ts, existing[0]))
            self._store.conn.commit()
            return existing[0]
        cur = self._store.conn.execute(
            "INSERT INTO a_to_b_candidates (a_source_type, a_source_id, a_title, a_content, a_strength, a_review_count, b_title, b_content, b_unit_type, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("card", card_id, card["title"], card["content"], card["memory_strength"],
             card["review_count"], b_title or card["title"], b_content or card["content"],
             b_unit_type, "pending", ts, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def publish(self, candidate_id: int) -> dict:
        cand = self._store.conn.execute("SELECT * FROM a_to_b_candidates WHERE id=?", (candidate_id,)).fetchone()
        if not cand: return {"error": "not found"}
        ts = datetime.now(timezone.utc).isoformat()
        # Create machine_knowledge_unit
        cur = self._store.conn.execute(
            "INSERT INTO machine_knowledge_units (title, content, unit_type, source_type, tags, confidence, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (cand["b_title"], cand["b_content"], cand["b_unit_type"], "a_to_b",
             f"card_{cand['a_source_id']}", cand["a_strength"], ts, ts))
        self._store.conn.execute("UPDATE a_to_b_candidates SET status='published', updated_at=? WHERE id=?", (ts, candidate_id))
        self._store.conn.commit()
        return {"knowledge_id": cur.lastrowid, "status": "published"}

    def list_candidates(self, status: str = "pending") -> list[dict]:
        cur = self._store.conn.execute("SELECT * FROM a_to_b_candidates WHERE status=? ORDER BY a_strength DESC", (status,))
        return [dict(r) for r in cur.fetchall()]
