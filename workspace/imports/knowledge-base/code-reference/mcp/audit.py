from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AuditEntry:
    tool: str
    user: str
    input: str
    status: str
    timestamp: str = ""
    duration_ms: float = 0.0


class AuditLog:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(self, entry: AuditEntry) -> None:
        if not entry.timestamp:
            entry.timestamp = datetime.now(timezone.utc).isoformat()
        self._entries.append(entry)

    def recent(self, limit: int = 20) -> list[AuditEntry]:
        return self._entries[-limit:]

    def clear(self) -> None:
        self._entries.clear()