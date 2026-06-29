from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

class MachineRouteEngine:
    def __init__(self, store: Any) -> None:
        self._store = store

    def create_route(self, goal: str, context_req: str = "", knowledge_req: str = "", tool_req: str = "") -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute("INSERT INTO machine_routes (goal, context_requirements, knowledge_requirements, tool_requirements, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)", (goal, context_req, knowledge_req, tool_req, ts, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def add_step(self, route_id: int, step_type: str, description: str, expected_output: str = "", order_num: int = 0) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute("INSERT INTO route_steps_b (route_id, step_type, description, expected_output, order_num, completed) VALUES (?, ?, ?, ?, ?, ?)", (route_id, step_type, description, expected_output, order_num, 0))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def get_route(self, route_id: int) -> dict:
        route = self._store.conn.execute("SELECT * FROM machine_routes WHERE id=?", (route_id,)).fetchone()
        if not route: return {}
        steps = self._store.conn.execute("SELECT * FROM route_steps_b WHERE route_id=? ORDER BY order_num", (route_id,)).fetchall()
        return {"route": dict(route), "steps": [dict(s) for s in steps]}

    def list_routes(self, limit: int = 20) -> list[dict]:
        cur = self._store.conn.execute("SELECT * FROM machine_routes ORDER BY updated_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]