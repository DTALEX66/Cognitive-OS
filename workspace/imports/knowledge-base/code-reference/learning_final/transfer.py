"""Transfer Engine - Cross-domain knowledge transfer ()"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
import json

class TransferSession:
    def __init__(self, source_domain: str, target_domain: str, evidence: dict):
        self.source_domain = source_domain
        self.target_domain = target_domain
        self.evidence = evidence
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.status = "pending"

class TransferEngine:
    """Cross-domain knowledge transfer engine """
    def __init__(self, store):
        self._store = store
        self._sessions = {}
    def create_session(self, source_domain, target_domain, knowledge_id=None):
        session_id = f"transfer_{int(datetime.now(timezone.utc).timestamp())}"
        self._sessions[session_id] = TransferSession(source_domain, target_domain, {"knowledge_id": knowledge_id})
        return session_id
    def bridge_knowledge(self, source_domain, target_domain, content, context=None):
        session_id = self.create_session(source_domain, target_domain)
        ts = datetime.now(timezone.utc).isoformat()
        self._store.conn.execute(
            "INSERT INTO cards (title, content, tags, memory_strength, next_review_at, created_at, updated_at) VALUES (?,?,?,0.8,?,?,?)",
            (f"[Transferred] {source_domain} -> {target_domain}", content,
             f"transfer,{source_domain},{target_domain}", ts, ts, ts))
        self._store.conn.commit()
        return {"session_id": session_id, "status": "bridged", "target_domain": target_domain}
    def get_session(self, session_id):
        return self._sessions.get(session_id)
    def list_transfers(self, limit=20):
        rows = self._store.conn.execute(
            "SELECT id, title, tags, created_at FROM cards WHERE tags LIKE '%transfer%' ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": r[0], "title": r[1], "tags": r[2], "created": r[3]} for r in rows]
