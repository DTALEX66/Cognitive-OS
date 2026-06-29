"""History Engine - conversation history management"""

from __future__ import annotations
from datetime import datetime, timezone
import json


class HistoryEngine:
    def __init__(self, store=None, max_entries=1000):
        self._store = store
        self._entries = []
        self._max = max_entries

    def append(self, entry):
        entry["_ts"] = datetime.now(timezone.utc).isoformat()
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]

    def query(self, q="", limit=20):
        if not q:
            return self._entries[-limit:]
        return [e for e in self._entries if q.lower() in json.dumps(e).lower()][-limit:]

    def since(self, ts):
        return [e for e in self._entries if e.get("_ts", "") >= ts]

    def clear(self):
        self._entries = []

    def count(self):
        return len(self._entries)
