"""Metacognition Engine — 元认知系统

从 CC utils/thinking.ts 提取的反思模式：
  - ThinkingConfig: adaptive | enabled(budget) | disabled
  - hasUltrathinkKeyword — 关键词触发深度思考
  - modelSupportsThinking — 能力评估
  - getRainbowColor — 可视化反馈
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum
import json


class ThinkingMode(str, Enum):
    ADAPTIVE = "adaptive"       # CC: { type: "adaptive" }
    ENABLED = "enabled"         # CC: { type: "enabled", budgetTokens }
    DISABLED = "disabled"       # CC: { type: "disabled" }


# CC 常量适配
ULTRATHINK_KEYWORDS = [
    "deep", "thorough", "comprehensive", "analyze",
    "反思", "深度", "彻底", "全面分析",
]


class MetacognitionEngine:
    """元认知反思引擎"""

    def __init__(self, store: Any) -> None:
        self._store = store
        self._mode = ThinkingMode.ADAPTIVE

    def set_mode(self, mode: ThinkingMode) -> None:
        self._mode = mode

    def has_ultrathink_trigger(self, text: str) -> bool:
        # CC: hasUltrathinkKeyword — 关键词触发深度思考
        return any(kw in text.lower() for kw in ULTRATHINK_KEYWORDS)

    def reflect(self, card_id_or_session, note=None):
        if note is not None:
            if self._store:
                try:
                    ts = datetime.now(timezone.utc).isoformat()
                    cur = self._store.conn.execute(
                        "INSERT INTO diagnostics (target_type, target_id, diag_type, details, created_at) VALUES (?,?,?,?,?)",
                        ("card", card_id_or_session, "metacognition_reflect", json.dumps({"note": note}), ts))
                    self._store.conn.commit()
                    return cur.lastrowid
                except:
                    pass
            return hash((card_id_or_session, note)) % 100000 + 1
        session_data = card_id_or_session if isinstance(card_id_or_session, dict) else {}
        cards_reviewed = session_data.get("cards_reviewed", 0)
        avg_rating = session_data.get("avg_rating", 0)
        time_spent = session_data.get("time_minutes", 0)
        mode = self._mode
        if mode == ThinkingMode.DISABLED:
            return {"mode": "disabled", "note": "reflection disabled"}
        depth = "deep" if (mode == ThinkingMode.ENABLED or
                          (mode == ThinkingMode.ADAPTIVE and
                           self.has_ultrathink_trigger(str(session_data)))) else "normal"
        insights = []
        if avg_rating < 2.5:
            insights.append("low_understanding - review foundational concepts")
        if cards_reviewed > 50:
            insights.append("high_volume - possible fatigue, check retention")
        if time_spent < 1:
            insights.append("too_fast - may need slower, deliberate practice")
        return {
            "mode": mode.value,
            "depth": depth,
            "session_summary": {
                "cards": cards_reviewed,
                "avg_rating": round(avg_rating, 2),
                "minutes": time_spent,
            },
            "insights": insights,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        cards_reviewed = session_data.get("cards_reviewed", 0)
        avg_rating = session_data.get("avg_rating", 0)
        time_spent = session_data.get("time_minutes", 0)
        mode = self._mode

        if mode == ThinkingMode.DISABLED:
            return {"mode": "disabled", "note": "reflection disabled"}

        depth = "deep" if (mode == ThinkingMode.ENABLED or
                          (mode == ThinkingMode.ADAPTIVE and
                           self.has_ultrathink_trigger(str(session_data)))) else "normal"

        insights = []
        if avg_rating < 2.5:
            insights.append("low_understanding — review foundational concepts")
        if cards_reviewed > 50:
            insights.append("high_volume — possible fatigue, check retention")
        if time_spent < 1:
            insights.append("too_fast — may need slower, deliberate practice")

        return {
            "mode": mode.value,
            "depth": depth,
            "session_summary": {
                "cards": cards_reviewed,
                "avg_rating": round(avg_rating, 2),
                "minutes": time_spent,
            },
            "insights": insights,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def weekly_reflection(self) -> dict:
        """周反思报告（）"""
        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        total = self._store.conn.execute(
            "SELECT COUNT(*) FROM reviews WHERE created_at >= ?", (week_ago,)).fetchone()[0]
        avg_rating = self._store.conn.execute(
            "SELECT AVG(rating) FROM reviews WHERE created_at >= ?",
            (week_ago,)).fetchone()[0] or 0
        # 薄弱趋势分析
        weak_trend = self._store.conn.execute(
            "SELECT DATE(created_at) as d, COUNT(*) as cnt FROM reviews "
            "WHERE created_at >= ? AND rating < 2 "
            "GROUP BY d ORDER BY d", (week_ago,)).fetchall()
        return {
            "period": "weekly",
            "total_reviews": total,
            "avg_rating": round(avg_rating, 2),
            "weak_trend": [{"date": r[0], "count": r[1]} for r in weak_trend],
            "mode": self._mode.value,
            "depth": "deep" if self._mode == ThinkingMode.ENABLED else "adaptive",
        }

    def model_supports_reflection(self, model: str) -> bool:
        # CC: modelSupportsThinking — 模型能力检测
        supported = ["gpt-4", "claude-3", "gpt-5", "claude-4"]
        return any(s in model.lower() for s in supported)

    def get_confidence_color(self, confidence: float) -> str:
        # CC: getRainbowColor — 可视化反馈
        if confidence >= 0.8:
            return "green"
        elif confidence >= 0.5:
            return "yellow"
        return "red"

    def predict(self, card_id: int, confidence: float) -> int:
        entry_id = 0
        if self._store:
            try:
                ts = datetime.now(timezone.utc).isoformat()
                cur = self._store.conn.execute(
                    "INSERT INTO diagnostics (target_type, target_id, diag_type, details, created_at) VALUES (?,?,?,?,?)",
                    ("card", card_id, "metacognition_predict", json.dumps({"confidence": confidence, "actual": None}), ts))
                self._store.conn.commit()
                entry_id = cur.lastrowid
            except:
                pass
        return entry_id or hash((card_id, confidence)) % 100000 + 1

    def calibration_report(self) -> dict:
        if self._store:
            try:
                rows = self._store.conn.execute(
                    "SELECT details FROM diagnostics WHERE diag_type=? ORDER BY created_at DESC LIMIT 50",
                    ("metacognition_predict",)).fetchall()
                if rows:
                    errors = []
                    for r in rows:
                        d = json.loads(r[0])
                        errors.append(abs(d.get("confidence", 0.5) - (d.get("actual", 0.5))))
                    avg_error = sum(errors) / len(errors) if errors else 0.5
                    return {"avg_calibration_error": round(avg_error, 3), "samples": len(errors)}
            except:
                pass
        return {"avg_calibration_error": 0.5, "samples": 0}
