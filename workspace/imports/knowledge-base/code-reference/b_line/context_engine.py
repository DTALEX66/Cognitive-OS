from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json

class ContextEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def build_pack(self, goal: str, knowledge_ids: list[int] = None, route_id: int = 0) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        k_ids = knowledge_ids or []
        total_conf = 0.0
        knowledge_snippets = []
        for kid in k_ids:
            row = self._store.conn.execute("SELECT confidence, title, content FROM machine_knowledge_units WHERE id=?", (kid,)).fetchone()
            if row:
                total_conf += row[0]
                knowledge_snippets.append({"id": kid, "title": row[1], "content_preview": row[2][:200] if row[2] else ""})
        avg_conf = total_conf / max(len(k_ids), 1)
        token_est = sum(len(s["content_preview"]) for s in knowledge_snippets) + len(goal) + 500
        pack_data = json.dumps({"goal": goal, "knowledge_snippets": knowledge_snippets, "total_units": len(k_ids)})
        cur = self._store.conn.execute("INSERT INTO context_packs (goal, knowledge_ids, route_id, pack_data, confidence_score, token_estimate, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (goal, json.dumps(k_ids), route_id, pack_data, round(avg_conf, 3), token_est, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def get_pack(self, pack_id: int) -> dict:
        row = self._store.conn.execute("SELECT * FROM context_packs WHERE id=?", (pack_id,)).fetchone()
        return dict(row) if row else {}