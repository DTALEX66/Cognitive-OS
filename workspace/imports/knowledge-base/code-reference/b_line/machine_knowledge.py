from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class MachineKnowledgeEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def create_unit(self, title: str, content: str = "", unit_type: str = "rule", tags: str = "", confidence: float = 0.5) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO machine_knowledge_units (title, content, unit_type, tags, confidence, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, content, unit_type, tags, confidence, ts, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def search(self, query: str, limit: int = 20) -> list[dict]:
        cur = self._store.conn.execute("SELECT * FROM machine_knowledge_units WHERE content LIKE ? OR tags LIKE ? ORDER BY confidence DESC LIMIT ?", (f"%{query}%", f"%{query}%", limit))
        return [dict(r) for r in cur.fetchall()]

    def get(self, unit_id: int) -> dict | None:
        row = self._store.conn.execute("SELECT * FROM machine_knowledge_units WHERE id=?", (unit_id,)).fetchone()
        return dict(row) if row else None

    def list_by_type(self, unit_type: str, limit: int = 20) -> list[dict]:
        cur = self._store.conn.execute("SELECT * FROM machine_knowledge_units WHERE unit_type=? ORDER BY confidence DESC LIMIT ?", (unit_type, limit))
        return [dict(r) for r in cur.fetchall()]