"""Understanding Engine - Knowledge Structure (System)"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum
import re

class KnowledgeNodeType(str, Enum):
    CONCEPT = "concept"
    FACT = "fact"
    PROCEDURE = "procedure"
    RELATION = "relation"
    DECISION = "decision"
    PATTERN = "pattern"
    RULE = "rule"
    EXAMPLE = "example"
    PREREQUISITE = "prerequisite"

class ContextCache:
    def __init__(self, ttl_seconds: int = 300):
        self._cache = {}
        self._ttl = ttl_seconds
    def get_or_compute(self, key, factory):
        now = datetime.now(timezone.utc).timestamp()
        if key in self._cache:
            val, ts = self._cache[key]
            if (now - ts) < self._ttl:
                return val
        val = factory()
        self._cache[key] = (val, now)
        return val
    def invalidate(self, key=None):
        if key: self._cache.pop(key, None)
        else: self._cache.clear()

class UnderstandingEngine:
    def __init__(self, store):
        self._store = store
        self._cache = ContextCache(ttl_seconds=120)
    def build_system_context(self):
        return self._cache.get_or_compute("system_context", lambda: {
            "node_count": self._store.conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0],
            "total_cards": self._store.conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0],
            "recent_nodes": [dict(r) for r in self._store.conn.execute("SELECT id, title, created_at FROM cards ORDER BY created_at DESC LIMIT 10").fetchall()],
        })
    def build_user_context(self):
        return self._cache.get_or_compute("user_context", lambda: {
            "current_date": datetime.now(timezone.utc).isoformat()[:10],
        })
    def classify_content(self, title, content, tags):
        cl = content.lower()
        if any(w in cl for w in ["how to", "method", "procedure", "??", "??"]):
            return KnowledgeNodeType.PROCEDURE
        if any(w in cl for w in ["?", "??", "definition"]):
            return KnowledgeNodeType.CONCEPT
        if any(w in cl for w in ["??", "??", "example"]):
            return KnowledgeNodeType.EXAMPLE
        if any(w in cl for w in ["??", "rule", "must"]):
            return KnowledgeNodeType.RULE
        if any(w in cl for w in ["??", "decision"]):
            return KnowledgeNodeType.DECISION
        if any(w in cl for w in ["??", "pattern"]):
            return KnowledgeNodeType.PATTERN
        if any(w in cl for w in ["??", "??", "causes"]):
            return KnowledgeNodeType.RELATION
        return KnowledgeNodeType.FACT
    def atomize(self, text):
        blocks = []
        paras = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
        for i, p in enumerate(paras):
            nt = self.classify_content("", p, "")
            blocks.append({"id": f"b_{i}", "content": p, "node_type": nt.value, "length": len(p)})
        return blocks
    def build_knowledge_graph(self, card_ids=None):
        if card_ids:
            ph = ",".join("?" * len(card_ids))
            rows = self._store.conn.execute(f"SELECT id, title, content, tags FROM cards WHERE id IN ({ph})", card_ids).fetchall()
        else:
            rows = self._store.conn.execute("SELECT id, title, content, tags FROM cards ORDER BY id DESC LIMIT 200").fetchall()
        nodes = [{"id": r[0], "label": r[1], "type": self.classify_content(r[1], r[2], r[3]).value, "tags": r[3].split(",") if r[3] else []} for r in rows]
        edges = []
        for i, r1 in enumerate(rows):
            for j, r2 in enumerate(rows):
                if i >= j: continue
                t1 = set(r1[3].split(",")) if r1[3] else set()
                t2 = set(r2[3].split(",")) if r2[3] else set()
                shared = t1 & t2
                if shared: edges.append({"source": r1[0], "target": r2[0], "shared": list(shared)})
        return {"nodes": nodes, "edges": edges[:100], "node_count": len(nodes), "edge_count": min(len(edges), 100)}
    def save_knowledge_node(self, title, content, node_type, tags=""):
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO cards (title, content, tags, memory_strength, next_review_at, created_at, updated_at) VALUES (?,?,?,1.0,?,?,?)",
            (title, content, tags, ts, ts, ts))
        self._store.conn.commit()
        return cur.lastrowid
