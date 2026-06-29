from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class TraceAudit:
    def __init__(self, store: Any) -> None:
        self._store = store

    def log(self, trace_type: str = "mcp_call", agent_role: str = "", tool_name: str = "", input_summary: str = "", output_summary: str = "", success: bool = True, duration_ms: int = 0, project: str = "") -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute("INSERT INTO execution_traces (trace_type, agent_role, tool_name, input_summary, output_summary, success, duration_ms, project_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (trace_type, agent_role, tool_name, input_summary, output_summary, 1 if success else 0, duration_ms, project, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def list_recent(self, limit: int = 20, trace_type: str = "") -> list[dict]:
        if trace_type:
            cur = self._store.conn.execute("SELECT * FROM execution_traces WHERE trace_type=? ORDER BY created_at DESC LIMIT ?", (trace_type, limit))
        else:
            cur = self._store.conn.execute("SELECT * FROM execution_traces ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

    def failure_summary(self) -> dict:
        total = self._store.conn.execute("SELECT COUNT(*) FROM execution_traces").fetchone()[0]
        failed = self._store.conn.execute("SELECT COUNT(*) FROM execution_traces WHERE success=0").fetchone()[0]
        return {"total": total, "failed": failed, "success_rate": round((total - failed) / max(total, 1), 3)}