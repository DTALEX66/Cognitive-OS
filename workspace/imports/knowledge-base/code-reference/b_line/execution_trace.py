"""B-Line Execution Trace - Detailed agent execution recording.

Records step-by-step execution with input/output snapshots,
duration tracking, parent-child trace relationships, and
aggregate statistics for performance analysis.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json


class ExecutionTraceEngine:
    """Enhanced execution trace with snapshots and hierarchical tracing.

    Records each step of agent execution including:
    - Input/output snapshots for reproducibility
    - Duration metrics for performance analysis
    - Parent-child trace trees for complex workflows
    - Tag-based filtering and search
    """

    def __init__(self, store: Any) -> None:
        self._store = store

    def start_trace(self, trace_type: str, agent_role: str = "",
                    tool_name: str = "", input_data: Any = None,
                    project: str = "", tags: str = "",
                    parent_trace_id: int = 0,
                    metadata: dict | None = None) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        input_snapshot = json.dumps(input_data, default=str) if input_data else ""
        meta_json = json.dumps(metadata or {})
        cur = self._store.conn.execute(
            "INSERT INTO execution_traces (trace_type, agent_role, tool_name,"
            " input_summary, input_snapshot, output_summary, output_snapshot,"
            " success, duration_ms, project_name, step_order, parent_trace_id,"
            " tags, metadata_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trace_type, agent_role, tool_name,
             self._summarize(input_snapshot), input_snapshot,
             "", "", 1, 0, project, 0, parent_trace_id,
             tags, meta_json, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def complete_trace(self, trace_id: int, output_data: Any = None,
                       success: bool = True, duration_ms: int = 0) -> bool:
        output_snapshot = json.dumps(output_data, default=str) if output_data else ""
        self._store.conn.execute(
            "UPDATE execution_traces SET output_summary=?, output_snapshot=?,"
            " success=?, duration_ms=? WHERE id=?",
            (self._summarize(output_snapshot), output_snapshot,
             1 if success else 0, duration_ms, trace_id))
        self._store.conn.commit()
        return True

    def record_step(self, trace_type: str, agent_role: str, tool_name: str,
                    input_data: Any = None, output_data: Any = None,
                    success: bool = True, duration_ms: int = 0,
                    step_order: int = 0, parent_trace_id: int = 0,
                    project: str = "", tags: str = "",
                    metadata: dict | None = None) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        input_snapshot = json.dumps(input_data, default=str) if input_data else ""
        output_snapshot = json.dumps(output_data, default=str) if output_data else ""
        meta_json = json.dumps(metadata or {})
        cur = self._store.conn.execute(
            "INSERT INTO execution_traces (trace_type, agent_role, tool_name,"
            " input_summary, input_snapshot, output_summary, output_snapshot,"
            " success, duration_ms, project_name, step_order, parent_trace_id,"
            " tags, metadata_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trace_type, agent_role, tool_name,
             self._summarize(input_snapshot), input_snapshot,
             self._summarize(output_snapshot), output_snapshot,
             1 if success else 0, duration_ms, project, step_order,
             parent_trace_id, tags, meta_json, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    # ── Legacy log compatibility ──

    def log(self, trace_type: str = "mcp_call", agent_role: str = "",
            tool_name: str = "", input_summary: str = "",
            output_summary: str = "", success: bool = True,
            duration_ms: int = 0, project: str = "",
            input_snapshot: str = "", output_snapshot: str = "",
            step_order: int = 0, parent_trace_id: int = 0,
            tags: str = "", metadata: dict | None = None) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        meta_json = json.dumps(metadata or {})
        cur = self._store.conn.execute(
            "INSERT INTO execution_traces (trace_type, agent_role, tool_name,"
            " input_summary, input_snapshot, output_summary, output_snapshot,"
            " success, duration_ms, project_name, step_order, parent_trace_id,"
            " tags, metadata_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (trace_type, agent_role, tool_name,
             input_summary, input_snapshot, output_summary, output_snapshot,
             1 if success else 0, duration_ms, project, step_order,
             parent_trace_id, tags, meta_json, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    # ── Query ──

    def get_trace(self, trace_id: int) -> dict | None:
        row = self._store.conn.execute(
            "SELECT * FROM execution_traces WHERE id=?", (trace_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        r["metadata_json"] = json.loads(r.get("metadata_json", "{}"))
        return r

    def list_recent(self, limit: int = 20, trace_type: str = "",
                    agent_role: str = "", success_only: bool | None = None) -> list[dict]:
        conditions = []
        params = []
        if trace_type:
            conditions.append("trace_type=?")
            params.append(trace_type)
        if agent_role:
            conditions.append("agent_role=?")
            params.append(agent_role)
        if success_only is not None:
            conditions.append("success=?")
            params.append(1 if success_only else 0)
        where = " AND ".join(conditions) if conditions else "1=1"
        cur = self._store.conn.execute(
            f"SELECT * FROM execution_traces WHERE {where} ORDER BY created_at DESC LIMIT ?",
            params + [limit])
        result = []
        for row in cur.fetchall():
            r = dict(row)
            r["metadata_json"] = json.loads(r.get("metadata_json", "{}"))
            result.append(r)
        return result

    def get_trace_tree(self, root_trace_id: int) -> dict:
        """Build a tree of traces starting from a root, following parent-child links."""
        root = self.get_trace(root_trace_id)
        if not root:
            return {"error": "trace not found", "trace_id": root_trace_id}

        children = self._store.conn.execute(
            "SELECT id FROM execution_traces WHERE parent_trace_id=? ORDER BY step_order",
            (root_trace_id,)).fetchall()

        tree = {
            "trace": root,
            "children": [],
        }
        for (child_id,) in children:
            tree["children"].append(self.get_trace_tree(child_id))
        return tree

    def get_children(self, parent_trace_id: int) -> list[dict]:
        cur = self._store.conn.execute(
            "SELECT * FROM execution_traces WHERE parent_trace_id=? ORDER BY step_order",
            (parent_trace_id,))
        return [dict(r) for r in cur.fetchall()]

    # ── Statistics ──

    def failure_summary(self) -> dict:
        total = self._store.conn.execute(
            "SELECT COUNT(*) FROM execution_traces").fetchone()[0] or 0
        failed = self._store.conn.execute(
            "SELECT COUNT(*) FROM execution_traces WHERE success=0").fetchone()[0] or 0
        return {
            "total": total, "failed": failed,
            "success_rate": round((total - failed) / max(total, 1), 3),
        }

    def duration_stats(self, trace_type: str = "",
                       agent_role: str = "") -> dict:
        conditions = []
        params = []
        if trace_type:
            conditions.append("trace_type=?")
            params.append(trace_type)
        if agent_role:
            conditions.append("agent_role=?")
            params.append(agent_role)
        where = " AND ".join(conditions) if conditions else "1=1"
        row = self._store.conn.execute(
            f"SELECT COUNT(*), AVG(duration_ms), MIN(duration_ms), MAX(duration_ms),"
            f" SUM(duration_ms) FROM execution_traces WHERE {where} AND duration_ms > 0",
            params).fetchone()
        return {
            "filter": {"trace_type": trace_type, "agent_role": agent_role},
            "count": row[0] or 0,
            "avg_ms": round(row[1] or 0, 1),
            "min_ms": row[2] or 0,
            "max_ms": row[3] or 0,
            "total_ms": row[4] or 0,
        }

    def role_stats(self) -> list[dict]:
        cur = self._store.conn.execute(
            "SELECT agent_role, COUNT(*) as cnt, AVG(duration_ms) as avg_dur,"
            " SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) as successes"
            " FROM execution_traces WHERE agent_role != ''"
            " GROUP BY agent_role ORDER BY cnt DESC")
        return [
            {"role": r[0], "total_calls": r[1],
             "avg_duration_ms": round(r[2] or 0, 1),
             "successes": r[3],
             "success_rate": round(r[3] / max(r[1], 1), 3)}
            for r in cur.fetchall()
        ]

    def search_traces(self, keyword: str, limit: int = 50) -> list[dict]:
        pattern = f"%{keyword}%"
        cur = self._store.conn.execute(
            "SELECT * FROM execution_traces WHERE input_summary LIKE ?"
            " OR output_summary LIKE ? OR tool_name LIKE ? OR tags LIKE ?"
            " ORDER BY created_at DESC LIMIT ?",
            (pattern, pattern, pattern, pattern, limit))
        return [dict(r) for r in cur.fetchall()]

    # ── Helpers ──

    @staticmethod
    def _summarize(text: str, max_len: int = 200) -> str:
        if not text:
            return ""
        if len(text) <= max_len:
            return text
        return text[:max_len - 3] + "..."


__all__ = ["ExecutionTraceEngine"]
