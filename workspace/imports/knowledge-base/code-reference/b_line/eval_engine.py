"""B线评估层 — 测试、RAG评估、红队"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json

class EvalEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def run(self, eval_type: str, target: str, input_data: str,
            expected: str, actual: str, model: str = "") -> dict:
        ts = datetime.now(timezone.utc).isoformat()
        from difflib import SequenceMatcher
        sim = SequenceMatcher(None, expected.lower(), actual.lower()).ratio()
        score = round(sim, 3)
        metrics = json.dumps({"similarity": score, "length_match": round(len(actual)/max(len(expected),1), 3)})
        cur = self._store.conn.execute(
            "INSERT INTO eval_runs (eval_type, target, input_data, expected_output, actual_output, score, metric_scores, model_used, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eval_type, target, input_data, expected, actual, score, metrics, model, ts))
        self._store.conn.commit()
        return {"run_id": cur.lastrowid, "score": score, "metrics": json.loads(metrics)}

    def summary(self, eval_type: str = "") -> dict:
        if eval_type:
            row = self._store.conn.execute("SELECT COUNT(*), AVG(score) FROM eval_runs WHERE eval_type=?", (eval_type,)).fetchone()
            typ = eval_type
        else:
            row = self._store.conn.execute("SELECT COUNT(*), AVG(score) FROM eval_runs").fetchone()
            typ = "all"
        return {"type": typ, "total_runs": row[0], "avg_score": round(row[1] or 0, 3)}

    def list_runs(self, eval_type: str = "", limit: int = 20) -> list[dict]:
        if eval_type:
            cur = self._store.conn.execute("SELECT * FROM eval_runs WHERE eval_type=? ORDER BY created_at DESC LIMIT ?", (eval_type, limit))
        else:
            cur = self._store.conn.execute("SELECT * FROM eval_runs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]
