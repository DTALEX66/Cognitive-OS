"""Diagnostics Engine — 学习诊断系统

5 种学习诊断策略：
  1. full — 全量诊断（对应 compactConversation）
  2. partial — 部分诊断（对应 partialCompactConversation）
  3. auto — 自动触发诊断（对应 autoCompact.ts）
  4. micro — 快速轻量诊断（对应 microCompact.ts）
  5. session — 会话记忆诊断（对应 sessionMemoryCompact.ts）
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
from enum import Enum
import json


class DiagnosticStrategy(str, Enum):
    FULL = "full"
    PARTIAL = "partial"
    AUTO = "auto"
    MICRO = "micro"
    SESSION = "session"


# MAX_OUTPUT_TOKENS_FOR_SUMMARY = 20_000 → MAX_DIAG_DEPTH
MAX_DIAG_DEPTH = 5  # 最大诊断递归深度
AUTO_DIAG_WINDOW = 0.7  # 自动诊断阈值（掌握度低于此值触发）


class DiagnosticsEngine:
    """学习诊断引擎 — 5 种诊断策略"""

    def __init__(self, store: Any) -> None:
        self._store = store

    # ── 策略 1: 全量诊断 ──────────────────────────────
    def full_diagnose(self, subject: str) -> dict:
        """全量诊断：全面扫描一个学科的所有知识点"""
        cards = self._store.conn.execute(
            "SELECT id, title, memory_strength FROM cards WHERE tags LIKE ? ORDER BY memory_strength ASC",
            (f"%{subject}%",)).fetchall()
        gaps = [{"id": r[0], "topic": r[1], "strength": r[2]}
                for r in cards if r[2] < 0.3]
        return {
            "strategy": "full",
            "subject": subject,
            "total": len(cards),
            "gaps": gaps[:20],
            "gap_count": len(gaps),
            "mastery": round(1 - len(gaps) / max(len(cards), 1), 3),
            "recommendations": [g["topic"] for g in gaps[:5]],
        }

    # ── 策略 2: 部分诊断 ──────────────────────────────
    def partial_diagnose(self, subject: str, recent_days: int = 7) -> dict:
        """部分诊断：只诊断最近 N 天新学的内容"""
        since = (datetime.now(timezone.utc) - timedelta(days=recent_days)).isoformat()
        cards = self._store.conn.execute(
            "SELECT c.id, c.title, c.memory_strength FROM cards c "
            "JOIN reviews r ON r.card_id = c.id "
            "WHERE c.tags LIKE ? AND r.created_at >= ?",
            (f"%{subject}%", since)).fetchall()
        gaps = [{"id": r[0], "topic": r[1], "strength": r[2]} for r in cards if r[2] < 0.4]
        return {
            "strategy": "partial",
            "subject": subject,
            "window_days": recent_days,
            "recent_cards": len(cards),
            "gaps": gaps[:10],
            "mastery": round(1 - len(gaps) / max(len(cards), 1), 3),
        }

    # ── 策略 3: 自动触发诊断 ──────────────────────────
    def auto_diagnose(self) -> Optional[dict]:
        """自动阈值触发诊断：检查所有低于阈值的知识点"""
        weak = self._store.conn.execute(
            "SELECT COUNT(*) FROM cards WHERE memory_strength < ?",
            (AUTO_DIAG_WINDOW,)).fetchone()[0]
        if weak == 0:
            return None
        subjects = self._store.conn.execute(
            "SELECT DISTINCT tags FROM cards WHERE memory_strength < ?",
            (AUTO_DIAG_WINDOW,)).fetchall()
        results = []
        for (tag,) in subjects:
            if tag:
                results.append(self.full_diagnose(tag))
        return {"trigger": f"{weak} weak cards", "diagnoses": results}

    # ── 策略 4: 微诊断 ────────────────────────────────
    def micro_diagnose(self, card_ids: list[int]) -> dict:
        """微诊断：针对指定卡片的快速检测"""
        placeholders = ",".join("?" for _ in card_ids)
        cards = self._store.conn.execute(
            f"SELECT id, title, memory_strength FROM cards WHERE id IN ({placeholders})",
            card_ids).fetchall()
        gaps = [{"id": r[0], "topic": r[1], "strength": r[2]} for r in cards if r[2] < 0.3]
        return {
            "strategy": "micro",
            "checked": len(cards),
            "issues": len(gaps),
            "gap_ids": [g["id"] for g in gaps],
        }

    # ── 策略 5: 会话记忆诊断 ──────────────────────────
    def session_diagnose(self, session_id: str) -> dict:
        """会话记忆诊断：分析一次学习会话中的薄弱环节"""
        reviews = self._store.conn.execute(
            "SELECT card_id, rating FROM reviews WHERE session_id = ?", (session_id,)).fetchall()
        if not reviews:
            return {"strategy": "session", "session_id": session_id, "note": "no data"}
        failed = [r[0] for r in reviews if r[1] < 2]
        cards = self._store.conn.execute(
            f"SELECT id, title FROM cards WHERE id IN ({','.join('?' for _ in failed)})",
            failed).fetchall() if failed else []
        return {
            "strategy": "session",
            "session_id": session_id,
            "total_reviews": len(reviews),
            "weak_cards": [{"id": r[0], "topic": r[1]} for r in cards],
        }

    # ── 历史记录 ─────────────────────────────────────
    def analyze(self, target_type: str, target_id: int, tags: list = None) -> dict:
        if tags:
            result = self.full_diagnose(tags[0]) if tags else {"mastery": 0.5}
        else:
            row = self._store.conn.execute(
                "SELECT memory_strength FROM cards WHERE id=?", (target_id,)).fetchone()
            result = {"mastery": row[0] if row else 0.5, "strategy": "full"}
        diagnostic_id = 0
        try:
            ts = datetime.now(timezone.utc).isoformat()
            cur = self._store.conn.execute(
                "INSERT INTO diagnostics (target_type, target_id, diag_type, details, created_at) VALUES (?,?,?,?,?)",
                (target_type, target_id, "analyze", json.dumps(result), ts))
            self._store.conn.commit()
            diagnostic_id = cur.lastrowid
        except:
            pass
        return {"mastery": result.get("mastery", 0.5), "diagnostic_id": diagnostic_id}

    def history(self, target_type: str, target_id: int) -> list[dict]:
        try:
            cur = self._store.conn.execute(
                "SELECT * FROM diagnostics WHERE target_type=? AND target_id=? ORDER BY created_at DESC",
                (target_type, target_id))
            return [dict(r) for r in cur.fetchall()]
        except:
            return []
