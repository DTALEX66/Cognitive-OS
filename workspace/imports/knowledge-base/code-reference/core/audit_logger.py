from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class AuditLogger:
    def __init__(self, store: Any) -> None:
        self._store = store

    def log(self, action: str, detail: str = "", user: str = "system") -> None:
        ts = datetime.now(timezone.utc).isoformat()
        try:
            self._store.log_event(action, detail, ts)
        except Exception:
            pass

    def recent(self, limit: int = 50) -> list[dict]:
        try:
            cur = self._store.conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(r) for r in cur.fetchall()]
        except Exception:
            return []