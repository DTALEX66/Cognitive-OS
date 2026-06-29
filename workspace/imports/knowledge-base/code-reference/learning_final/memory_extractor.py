"""Memory Extractor - auto memory extraction from CC extractMemories.ts"""

from __future__ import annotations
from datetime import datetime, timezone
import re


class MemoryExtractor:
    def __init__(self, store=None):
        self._store = store

    def extract(self, text, source=""):
        memories = []
        sentences = re.split(r"[.!?]+", text)
        for s in sentences:
            s = s.strip()
            if len(s) > 20 and any(
                w in s.lower() for w in ["remember", "learn", "import", "key", "important", "note"]
            ):
                memories.append(
                    {
                        "text": s[:200],
                        "source": source,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }
                )
        return memories
