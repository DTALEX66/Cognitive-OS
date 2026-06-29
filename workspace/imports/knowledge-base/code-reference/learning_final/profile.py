"""Profile Engine — 学习画像系统

学习画像追踪模式：
  - getStoredSessionCosts → 获取学习画像
  - saveCurrentSessionCosts → 保存每日画像
  - formatTotalCost → 生成统计报表
  - addToTotalSessionCost → 累加学习记录
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any, Optional
import json


class LearningProfile:
    """学习画像追踪器"""

    def __init__(self, store: Any) -> None:
        self._store = store

    # CC: saveCurrentSessionCosts
    def save_daily_profile(self, session_data: dict) -> int:
        today = datetime.now(timezone.utc).isoformat()[:10]
        existing = self._store.conn.execute(
            "SELECT id FROM profile_records WHERE date = ?", (today,)).fetchone()
        data = json.dumps({
            "subjects": session_data.get("subjects", []),
            "reviewed": session_data.get("cards_reviewed", 0),
            "new_cards": session_data.get("new_cards", 0),
            "accuracy": session_data.get("accuracy", 0),
            "time_minutes": session_data.get("time_minutes", 0),
            "weak_points": session_data.get("weak_points", []),
        })
        if existing:
            self._store.conn.execute(
                "UPDATE profile_records SET data = ?, updated_at = ? WHERE id = ?",
                (data, datetime.now(timezone.utc).isoformat(), existing[0]))
            self._store.conn.commit()
            return existing[0]
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO profile_records (date, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (today, data, ts, ts))
        self._store.conn.commit()
        return cur.lastrowid

    # CC: addToTotalSessionCost
    def add_review_record(self, subject: str, rating: int, time_sec: int) -> None:
        self._store.conn.execute(
            "INSERT INTO reviews (card_id, rating, created_at) "
            "VALUES ((SELECT id FROM cards WHERE title LIKE ? LIMIT 1), ?, ?)",
            (f"%{subject}%", rating, datetime.now(timezone.utc).isoformat()))
        self._store.conn.commit()

    # CC: getStoredSessionCosts
    def get_weekly_profile(self) -> dict:
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        records = self._store.conn.execute(
            "SELECT date, data FROM profile_records WHERE date >= ? ORDER BY date",
            (week_ago[:10],)).fetchall()
        days = []
        totals = {"reviewed": 0, "new_cards": 0, "time_minutes": 0}
        for r in records:
            d = json.loads(r[1])
            days.append({"date": r[0], **d})
            totals["reviewed"] += d.get("reviewed", 0)
            totals["new_cards"] += d.get("new_cards", 0)
            totals["time_minutes"] += d.get("time_minutes", 0)
        return {"period": "weekly", "days": days, "totals": totals}

    # CC: formatTotalCost
    def get_monthly_report(self) -> dict:
        month_ago = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        records = self._store.conn.execute(
            "SELECT date, data FROM profile_records WHERE date >= ? ORDER BY date",
            (month_ago[:10],)).fetchall()
        return {
            "period": "monthly",
            "total_days": len(records),
            "data": [json.loads(r[1]) for r in records],
        }




class LearnerProfile:
    def __init__(self, store=None):
        self.store = store
    
    def recalculate(self):
        if self.store:
            try:
                total = self.store.conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
                avg = self.store.conn.execute("SELECT AVG(memory_strength) FROM cards").fetchone()[0] or 0.0
                return {"total_cards": total, "avg_memory_strength": round(avg, 3)}
            except:
                pass
        return {"total_cards": 0, "avg_memory_strength": 0.0}
    
    def recommendations(self):
        if self.store:
            try:
                weak = self.store.conn.execute(
                    "SELECT id, title FROM cards WHERE memory_strength < 0.3 ORDER BY memory_strength ASC LIMIT 5").fetchall()
                return [{"id": r[0], "title": r[1]} for r in weak]
            except:
                pass
        return []
