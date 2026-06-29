"""B-Line Feedback Loop — Failure pattern recording, B->A knowledge feedback"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class FeedbackLoop:
    def __init__(self, store: Any) -> None:
        self._store = store

    def record_failure(self, title: str, pattern: str = "", symptoms: str = "",
                       root_cause: str = "", solution: str = "",
                       severity: int = 3, source_trace_id: int = 0) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO anti_patterns (title, pattern, symptoms, root_cause, solution, severity, source_trace_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, pattern, symptoms, root_cause, solution, severity, source_trace_id, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def feedback_to_a(self, anti_pattern_id: int) -> dict:
        ap = self._store.conn.execute("SELECT * FROM anti_patterns WHERE id=?", (anti_pattern_id,)).fetchone()
        if not ap:
            return {"error": "not found"}
        from pk_radar.core.learning_system import LearningSystem
        ls = LearningSystem(self._store)
        cid = ls.create_card(
            title="[B-Feedback] " + ap["title"],
            content="Pattern: " + ap["pattern"] + "\nSymptoms: " + ap["symptoms"] + "\nRoot Cause: " + ap["root_cause"] + "\nSolution: " + ap["solution"],
            deck="b_feedback", tags="b_feedback,severity_" + str(ap["severity"]))
        return {"card_id": cid, "source_anti_pattern_id": anti_pattern_id,
                "title": ap["title"], "severity": ap["severity"]}

    def list_anti_patterns(self, severity: int = 0, limit: int = 20) -> list[dict]:
        if severity > 0:
            cur = self._store.conn.execute(
                "SELECT * FROM anti_patterns WHERE severity >= ? ORDER BY severity DESC, created_at DESC LIMIT ?",
                (severity, limit))
        else:
            cur = self._store.conn.execute("SELECT * FROM anti_patterns ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]
    def analyze_trends(self):
        trends = {}
        trends["total_anti_patterns"] = len(self._anti_patterns)
        trends["by_severity"] = {}
        for ap in self._anti_patterns:
            sev = ap.get("severity", "unknown")
            trends["by_severity"][sev] = trends["by_severity"].get(sev, 0) + 1
        pattern_counts = {}
        for ap in self._anti_patterns:
            p = ap.get("pattern", "unknown")
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
        sorted_p = sorted(pattern_counts.items(), key=lambda x: -x[1])
        trends["common_patterns"] = [{"pattern": p, "count": c} for p, c in sorted_p[:5]]
        return trends
    def autofeedback(self):
        if not self._anti_patterns:
            return []
        suggestions = []
        for ap in self._anti_patterns[-10:]:
            pattern = ap.get("pattern", "")
            sev = ap.get("severity", "medium")
            if sev in ("high", "critical") and pattern:
                suggestions.append({"based_on": pattern, "suggestion": "Check for: " + pattern, "priority": "high" if sev == "critical" else "medium"})
        return suggestions
