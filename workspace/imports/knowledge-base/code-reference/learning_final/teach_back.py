"""Teach-Back Engine - Feynman technique """
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
import json

class TeachBackEngine:
    def __init__(self, store=None):
        self._store = store
        self._methods = ["feynman", "analogy", "simplify", "code_demo", "visual_map"]
    def list_methods(self):
        return self._methods
    def submit_explanation(self, concept: str, explanation: str, parent_id: int = None) -> dict:
        return self.save(concept, explanation, parent_id, "beginner")
    def save(self, source_type: str, source_id=0, audience_level="beginner", explanation="") -> int:
        if self._store:
            ts = datetime.now(timezone.utc).isoformat()
            feynman = feynman_score(len(explanation) / 500 if explanation else 0, 0.5, 0.5)
            cur = self._store.conn.execute(
                "INSERT INTO teach_back_sessions (source_type, source_id, audience_level, explanation, feynman_score, gaps_json, created_at) VALUES (?,?,?,?,?,?,?)",
                (source_type, source_id, audience_level, explanation, feynman, "[]", ts))
            self._store.conn.commit()
            return cur.lastrowid
        return 0
    def get(self, session_id: int) -> dict:
        if self._store:
            row = self._store.conn.execute(
                "SELECT id, source_type, source_id, audience_level, explanation, feynman_score, created_at FROM teach_back_sessions WHERE id=?",
                (session_id,)).fetchone()
            if row:
                return {"id": row[0], "source_type": row[1], "source_id": row[2], "audience_level": row[3], "explanation": row[4], "feynman_score": row[5], "created_at": row[6]}
        return None
    def list(self):
        if self._store:
            rows = self._store.conn.execute(
                "SELECT id, source_type, source_id, audience_level, explanation, feynman_score, created_at FROM teach_back_sessions ORDER BY created_at DESC LIMIT 100").fetchall()
            return [{"id": r[0], "source_type": r[1], "source_id": r[2], "audience_level": r[3], "explanation": r[4][:200], "feynman_score": r[5], "created_at": r[6]} for r in rows]
        return []
    def list_explanations(self, concept: str = "", limit: int = 20):
        return self.list()[:limit]
    def evaluate_clarity(self, explanation_id: int) -> dict:
        if self._store:
            row = self._store.conn.execute("SELECT id, explanation FROM teach_back_sessions WHERE id=?", (explanation_id,)).fetchone()
            if not row: return {"error": "not found"}
            text = row[1]
            clarity = min(1.0, len(text) / 1000) if text else 0.0
            gaps = []
            if len(text) < 100: gaps.append("too brief")
            if "because" not in text.lower() and "??" not in text: gaps.append("missing reasoning")
            self._store.conn.execute("UPDATE teach_back_sessions SET feynman_score=?, gaps_json=? WHERE id=?", (clarity, json.dumps(gaps), explanation_id))
            self._store.conn.commit()
            return {"id": explanation_id, "clarity_score": round(clarity, 2), "gaps": gaps}
        return {"id": explanation_id, "clarity_score": 0.5, "gaps": []}


def feynman_score(correctness=0.5, simplicity=0.5, completeness=0.5):
    return round((correctness * 0.4 + simplicity * 0.3 + completeness * 0.3), 3)
