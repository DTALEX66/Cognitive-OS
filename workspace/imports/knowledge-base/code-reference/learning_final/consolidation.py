"""Consolidation Engine - enhanced with CC compact system patterns (long-term consolidation)"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from enum import Enum
import json


class ConsolidationStrategy(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    INCREMENTAL = "incremental"
    MEMORY = "memory"
    MICRO = "micro"


POST_COMPACT_MAX_FILES = 5
POST_COMPACT_TOKEN_BUDGET = 50_000
WEAK_THRESHOLD = 0.3
DECAY_DAYS = 30


class ConsolidationEngine:
    """Consolidation engine with 5 strategies + daily/weekly reports."""

    def __init__(self, store=None):
        self._store = store
        self._compact_threshold = 0.75

    def full_compact(self, messages):
        total_tokens = sum(len(m.get("content","")) for m in messages)
        summary = self._gen(messages)
        return {"mode": "full", "original": len(messages), "summary": summary, "tokens_saved": total_tokens // 2}

    def micro_compact(self, new_msgs, existing=""):
        summary = self._gen(new_msgs)
        combined = existing + chr(10) + summary if existing else summary
        return {"mode": "micro", "new": len(new_msgs), "summary": combined}

    def session_compact(self, sessions):
        summaries = []
        for s in sessions:
            summaries.append(s.get("summary", s.get("result", ""))[:200])
        return {"mode": "session", "count": len(sessions), "summaries": summaries}

    def should_compact(self, current, maximum):
        ratio = current / maximum if maximum > 0 else 0
        return {"should": ratio >= self._compact_threshold, "ratio": ratio}

    def set_threshold(self, t):
        self._compact_threshold = max(0.1, min(0.99, t))

    def strip_attachments(self, messages):
        return [m for m in messages if "data:image" not in m.get("content","") and "data:audio" not in m.get("content","")]

    def _gen(self, messages):
        text = " ".join(m.get("content","")[:500] for m in messages[-10:] if m.get("content"))
        return text[:1000] if text else "(empty)"

    def list_schedules(self):
        if self._store:
            rows = self._store.conn.execute("SELECT id, method, created_at FROM teach_back_sessions ORDER BY created_at DESC LIMIT 20").fetchall()
            return [{"id": r[0], "method": r[1], "created": r[2]} for r in rows]
        return []

    def run_consolidation(self, method="weekly"):
        return self.micro_compact([{"content": "run: " + method}])

    def weekly_consolidate(self) -> dict:
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        weak = []
        if self._store:
            try:
                weak = self._store.conn.execute(
                    "SELECT id, title, memory_strength, next_review_at FROM cards "
                    "WHERE memory_strength < ? AND next_review_at <= ? "
                    "ORDER BY memory_strength ASC LIMIT ?",
                    (WEAK_THRESHOLD, week_ago, POST_COMPACT_MAX_FILES)).fetchall()
            except:
                pass
        plan = [{"id": r[0], "topic": r[1], "strength": r[2]} for r in weak]
        return {"strategy": "weekly", "period": "7d", "targets": plan, "total": len(plan), "priority": 1.0 if len(plan) > 5 else 0.5}

    def monthly_consolidate(self) -> dict:
        month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        stale = []
        if self._store:
            try:
                stale = self._store.conn.execute(
                    "SELECT id, title, memory_strength FROM cards WHERE "
                    "(SELECT MAX(created_at) FROM reviews WHERE card_id = cards.id) < ? "
                    "OR (SELECT MAX(created_at) FROM reviews WHERE card_id = cards.id) IS NULL",
                    (month_ago,)).fetchall()
            except:
                pass
        forgotten = [{"id": r[0], "topic": r[1], "strength": r[2]} for r in stale if r[2] < 0.3]
        return {"strategy": "monthly", "period": "30d", "stale_count": len(forgotten), "stale_topics": [f["topic"] for f in forgotten[:10]], "recommendation": "relearn" if len(forgotten) > 20 else "review"}

    def incremental_consolidate(self, since_days: int = 1) -> dict:
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).isoformat()
        new_cards = []
        if self._store:
            try:
                new_cards = self._store.conn.execute(
                    "SELECT c.id, c.title, c.memory_strength FROM cards c "
                    "JOIN reviews r ON r.card_id = c.id "
                    "WHERE r.created_at >= ? GROUP BY c.id HAVING c.memory_strength < ?",
                    (since, WEAK_THRESHOLD)).fetchall()
            except:
                pass
        return {"strategy": "incremental", "window": f"{since_days}d", "new_weak": len(new_cards), "items": [{"id": r[0], "topic": r[1]} for r in new_cards]}

    def memory_consolidate(self, card_ids: list[int]) -> dict:
        if not self._store:
            return {"strategy": "memory", "consolidated": 0, "details": []}
        placeholders = ",".join("?" for _ in card_ids)
        try:
            cards = self._store.conn.execute(
                f"SELECT id, title, memory_strength, tags FROM cards WHERE id IN ({placeholders})",
                card_ids).fetchall()
        except:
            return {"strategy": "memory", "consolidated": 0, "details": []}
        results = []
        for c in cards:
            new_strength = min(1.0, c[2] + 0.15)
            try:
                self._store.conn.execute("UPDATE cards SET memory_strength = ?, updated_at = ? WHERE id = ?",
                    (new_strength, datetime.now(timezone.utc).isoformat(), c[0]))
            except:
                pass
            results.append({"id": c[0], "topic": c[1], "before": c[2], "after": new_strength})
        if self._store:
            try:
                self._store.conn.commit()
            except:
                pass
        return {"strategy": "memory", "consolidated": len(results), "details": results}

    def micro_consolidate(self) -> dict:
        due = 0
        if self._store:
            try:
                today = datetime.now(timezone.utc).isoformat()[:10]
                due = self._store.conn.execute("SELECT COUNT(*) FROM cards WHERE next_review_at <= ?", (today,)).fetchone()[0]
            except:
                pass
        return {"strategy": "micro", "due_today": due, "estimated_minutes": due * 2}

    def daily_report(self) -> dict:
        if not self._store:
            return {"date": datetime.now(timezone.utc).isoformat()[:10], "cards_due": 0, "priority": 0.0}
        w = self.weekly_consolidate()
        m = self.micro_consolidate()
        return {"date": datetime.now(timezone.utc).isoformat()[:10], "cards_due": m["due_today"], "weekly_targets": w["total"], "due_today": m["due_today"], "priority": round(0.6 * min(w["total"] / 10, 1) + 0.4 * min(m["due_today"] / 20, 1), 3)}

    def weekly_report(self) -> dict:
        if not self._store:
            return {"period": "", "total_reviews": 0, "avg_strength": 0.0, "total_cards": 0}
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        total = 0
        avg = 0.0
        total_cards = 0
        try:
            total = self._store.conn.execute("SELECT COUNT(*) FROM reviews WHERE created_at >= ?", (week_ago,)).fetchone()[0]
            avg = self._store.conn.execute("SELECT AVG(memory_strength) FROM cards").fetchone()[0] or 0.0
            total_cards = self._store.conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
        except:
            pass
        return {"period": f"{week_ago[:10]} ~ {datetime.now(timezone.utc).isoformat()[:10]}", "total_reviews": total, "reviews": total, "avg_strength": round(avg, 3), "total_cards": total_cards}


def consolidation_priority(mastery_gain=0.5, forgetting_risk=0.5):
    return round((mastery_gain * 0.5 + forgetting_risk * 0.5), 3)
