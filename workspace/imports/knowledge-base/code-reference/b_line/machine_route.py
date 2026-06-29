"""B-Line Machine Route - FSM-based state machine routing engine.

Routes tasks through a state machine with conditional branching,
priority scoring, and fallback chains.
"""

from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import json


class RouteState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    EXECUTING = "executing"
    VALIDATING = "validating"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"
    FALLBACK = "fallback"
    RETRYING = "retrying"


class StepType(Enum):
    RETRIEVE = "retrieve"
    TRANSFORM = "transform"
    GENERATE = "generate"
    VALIDATE = "validate"
    CONDITION = "condition"
    PARALLEL = "parallel"
    CALLBACK = "callback"


STATE_TRANSITIONS = {
    RouteState.IDLE: {RouteState.PLANNING, RouteState.FAILED},
    RouteState.PLANNING: {RouteState.RETRIEVING, RouteState.EXECUTING, RouteState.FAILED},
    RouteState.RETRIEVING: {RouteState.EXECUTING, RouteState.FALLBACK, RouteState.FAILED},
    RouteState.EXECUTING: {RouteState.VALIDATING, RouteState.EVALUATING, RouteState.RETRYING, RouteState.FALLBACK, RouteState.FAILED},
    RouteState.VALIDATING: {RouteState.EVALUATING, RouteState.RETRYING, RouteState.FAILED},
    RouteState.EVALUATING: {RouteState.COMPLETED, RouteState.RETRYING, RouteState.FALLBACK, RouteState.FAILED},
    RouteState.RETRYING: {RouteState.EXECUTING, RouteState.FAILED},
    RouteState.FALLBACK: {RouteState.EXECUTING, RouteState.COMPLETED, RouteState.FAILED},
    RouteState.COMPLETED: set(),
    RouteState.FAILED: {RouteState.RETRYING},
}


class RouteContext:
    def __init__(self, goal, metadata=None):
        self.goal = goal
        self.metadata = metadata or {}
        self.variables = {}
        self.history = []
        self.errors = []

    def set(self, key, value):
        self.variables[key] = value

    def get(self, key, default=None):
        return self.variables.get(key, default)

    def record_step(self, step_type, detail, result=None):
        self.history.append({
            "step_type": step_type, "detail": detail,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def add_error(self, error):
        self.errors.append(error)

    def to_dict(self):
        return {
            "goal": self.goal, "metadata": self.metadata,
            "variables": self.variables, "history": self.history,
            "errors": self.errors,
        }


class RouteMatcher:
    def __init__(self, store):
        self._store = store

    def score_route(self, goal, route):
        score = 0.0
        goal_lower = goal.lower()
        route_goal_lower = route.get("goal", "").lower()
        tags = route.get("tags", "")
        goal_words = set(goal_lower.split())
        route_words = set(route_goal_lower.split())
        overlap = goal_words & route_words
        if overlap:
            score += len(overlap) / max(len(goal_words), 1) * 50.0
        if tags:
            tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
            for tag in tag_list:
                if tag in goal_lower:
                    score += 15.0
        context_req = route.get("context_requirements", "").lower()
        if context_req:
            for w in context_req.split(","):
                w = w.strip()
                if w and w in goal_lower:
                    score += 10.0
        priority = route.get("priority", 5)
        score += (10 - priority) * 2.0
        return round(score, 2)

    def find_best_route(self, goal, context=None):
        cur = self._store.conn.execute(
            "SELECT * FROM machine_routes WHERE status='active' ORDER BY priority ASC")
        routes = [dict(r) for r in cur.fetchall()]
        if not routes:
            return None
        scored = [(self.score_route(goal, r), r) for r in routes]
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_route = scored[0]
        if best_score < 5.0:
            return None
        return best_route

    def list_candidates(self, goal, min_score=5.0):
        cur = self._store.conn.execute(
            "SELECT * FROM machine_routes WHERE status='active' ORDER BY priority ASC")
        routes = [dict(r) for r in cur.fetchall()]
        scored = [(self.score_route(goal, r), r) for r in routes]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{"score": s, "route": r} for s, r in scored if s >= min_score]


class MachineRouteEngineV2:
    def __init__(self, store):
        self._store = store
        self._matcher = RouteMatcher(store)
        self._active_contexts = {}

    def create_route(self, goal, context_req="", knowledge_req="",
                     tool_req="", priority=5, tags="", fallback_route_id=0):
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO machine_routes (goal, context_requirements, knowledge_requirements,"
            " tool_requirements, fsm_state, priority, tags, fallback_route_id, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (goal, context_req, knowledge_req, tool_req, RouteState.IDLE.value,
             priority, tags, fallback_route_id, ts, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def get_route(self, route_id):
        route = self._store.conn.execute(
            "SELECT * FROM machine_routes WHERE id=?", (route_id,)).fetchone()
        if not route:
            return {}
        steps = self._store.conn.execute(
            "SELECT * FROM route_steps_b WHERE route_id=? ORDER BY order_num",
            (route_id,)).fetchall()
        return {"route": dict(route), "steps": [dict(s) for s in steps]}

    def list_routes(self, limit=20, state=""):
        if state:
            cur = self._store.conn.execute(
                "SELECT * FROM machine_routes WHERE fsm_state=? ORDER BY updated_at DESC LIMIT ?",
                (state, limit))
        else:
            cur = self._store.conn.execute(
                "SELECT * FROM machine_routes ORDER BY updated_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

    def update_state(self, route_id, new_state):
        route = self._store.conn.execute(
            "SELECT fsm_state FROM machine_routes WHERE id=?", (route_id,)).fetchone()
        if not route:
            return False
        current = RouteState(route["fsm_state"])
        if new_state not in STATE_TRANSITIONS.get(current, set()):
            return False
        ts = datetime.now(timezone.utc).isoformat()
        self._store.conn.execute(
            "UPDATE machine_routes SET fsm_state=?, updated_at=? WHERE id=?",
            (new_state.value, ts, route_id))
        self._store.conn.commit()
        return True

    def add_step(self, route_id, step_type, description, expected_output="",
                 order_num=0, condition_expr="", on_success_step_id=0,
                 on_failure_step_id=0, max_retries=3, timeout_ms=30000):
        cur = self._store.conn.execute(
            "INSERT INTO route_steps_b (route_id, step_type, description, expected_output,"
            " order_num, completed, condition_expr, on_success_step_id, on_failure_step_id,"
            " max_retries, timeout_ms) VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?)",
            (route_id, step_type, description, expected_output, order_num,
             condition_expr, on_success_step_id, on_failure_step_id, max_retries, timeout_ms))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def complete_step(self, step_id, success=True):
        self._store.conn.execute(
            "UPDATE route_steps_b SET completed=? WHERE id=?",
            (1 if success else 0, step_id))
        self._store.conn.commit()

    def evaluate_condition(self, expr, context):
        if not expr:
            return True
        expr = expr.strip()
        if expr.startswith("has:"):
            key = expr[4:].strip()
            return key in context.variables
        if expr.startswith("error_count"):
            parts = expr.split()
            if len(parts) == 3:
                threshold = int(parts[2])
                if parts[1] == ">": return len(context.errors) > threshold
                if parts[1] == "<": return len(context.errors) < threshold
                if parts[1] == ">=": return len(context.errors) >= threshold
            return False
        if expr.startswith("history_length"):
            parts = expr.split()
            if len(parts) == 3:
                threshold = int(parts[2])
                if parts[1] == ">": return len(context.history) > threshold
            return False
        for op in [">=", "<=", "!=", "==", ">", "<"]:
            if op in expr:
                left, right = expr.split(op, 1)
                left, right = left.strip(), right.strip()
                var_val = context.get(left)
                if var_val is None:
                    return False
                try:
                    left_num, right_num = float(var_val), float(right)
                    if op == ">": return left_num > right_num
                    if op == "<": return left_num < right_num
                    if op == ">=": return left_num >= right_num
                    if op == "<=": return left_num <= right_num
                    if op == "==": return left_num == right_num
                    if op == "!=": return left_num != right_num
                except (ValueError, TypeError):
                    pass
                right_str = right.strip("'\"")
                if op == "==": return str(var_val) == right_str
                if op == "!=": return str(var_val) != right_str
                return False
        if " in " in expr:
            left, right = expr.split(" in ", 1)
            left, right = left.strip(), right.strip()
            var_val = str(context.get(left, ""))
            try:
                items = json.loads(right)
                return var_val in [str(i) for i in items]
            except (json.JSONDecodeError, TypeError):
                pass
            return var_val in right
        return False

    def resolve_route(self, goal, context=None):
        ctx = context or RouteContext(goal)
        best = self._matcher.find_best_route(goal, ctx)
        if not best:
            return {"status": "no_route", "goal": goal, "candidates": 0}
        route_id = best["id"]
        self._active_contexts[route_id] = ctx
        self.update_state(route_id, RouteState.PLANNING)
        return {
            "status": "route_found", "route_id": route_id,
            "goal": best["goal"],
            "score": self._matcher.score_route(goal, best),
            "state": RouteState.PLANNING.value,
        }

    def get_next_step(self, route_id):
        steps = self._store.conn.execute(
            "SELECT * FROM route_steps_b WHERE route_id=? AND completed=0"
            " ORDER BY order_num LIMIT 1", (route_id,)).fetchone()
        if not steps:
            return None
        step = dict(steps)
        ctx = self._active_contexts.get(route_id)
        if step.get("condition_expr") and ctx:
            if not self.evaluate_condition(step["condition_expr"], ctx):
                self._store.conn.execute(
                    "UPDATE route_steps_b SET completed=-1 WHERE id=?", (step["id"],))
                self._store.conn.commit()
                return self.get_next_step(route_id)
        return step

    def execute_step(self, route_id, step_id, success, output=""):
        self.complete_step(step_id, success)
        ctx = self._active_contexts.get(route_id)
        if ctx:
            ctx.record_step("step_exec",
                "step %d: %s" % (step_id, "ok" if success else "fail"), output)
        next_step = self.get_next_step(route_id)
        if next_step:
            return {"status": "continue", "next_step": next_step}
        self.update_state(route_id, RouteState.COMPLETED)
        return {"status": "completed", "route_id": route_id}

    def handle_fallback(self, route_id, error):
        route = self._store.conn.execute(
            "SELECT * FROM machine_routes WHERE id=?", (route_id,)).fetchone()
        if not route:
            return {"status": "error", "detail": "route not found"}
        route_dict = dict(route)
        self.update_state(route_id, RouteState.FALLBACK)
        ctx = self._active_contexts.get(route_id)
        if ctx:
            ctx.add_error(error)
        fallback_id = route_dict.get("fallback_route_id", 0)
        if fallback_id > 0:
            fallback = self._store.conn.execute(
                "SELECT * FROM machine_routes WHERE id=?", (fallback_id,)).fetchone()
            if fallback:
                self._active_contexts[fallback_id] = ctx
                return {
                    "status": "fallback_activated",
                    "fallback_route_id": fallback_id,
                    "original_route_id": route_id,
                }
        return {"status": "no_fallback", "route_id": route_id, "error": error}

    def retry_route(self, route_id):
        self._store.conn.execute(
            "UPDATE route_steps_b SET completed=0 WHERE route_id=? AND completed=1",
            (route_id,))
        self._store.conn.commit()
        self.update_state(route_id, RouteState.RETRYING)
        return {"status": "retrying", "route_id": route_id}

    def get_context(self, route_id):
        return self._active_contexts.get(route_id)

    def clear_context(self, route_id):
        self._active_contexts.pop(route_id, None)

    def export_route_graph(self, route_id):
        route_data = self.get_route(route_id)
        if not route_data:
            return {"error": "route not found"}
        route = route_data["route"]
        steps = route_data["steps"]
        nodes = [{"id": "start", "label": route["goal"], "type": "start"}]
        edges = []
        for i, step in enumerate(steps):
            node_id = "step_%d" % step["id"]
            nodes.append({
                "id": node_id, "label": step["description"],
                "type": step["step_type"],
                "condition": step.get("condition_expr", ""),
            })
            prev_id = "step_%d" % steps[i - 1]["id"] if i > 0 else "start"
            edges.append({"from": prev_id, "to": node_id, "label": ""})
            if step.get("on_success_step_id"):
                edges.append({
                    "from": node_id,
                    "to": "step_%d" % step["on_success_step_id"],
                    "label": "success",
                })
            if step.get("on_failure_step_id"):
                edges.append({
                    "from": node_id,
                    "to": "step_%d" % step["on_failure_step_id"],
                    "label": "failure",
                })
        return {
            "route_id": route_id, "goal": route["goal"],
            "state": route.get("fsm_state", "idle"),
            "nodes": nodes, "edges": edges, "step_count": len(steps),
        }


__all__ = [
    "RouteState", "StepType", "STATE_TRANSITIONS",
    "RouteContext", "RouteMatcher", "MachineRouteEngineV2",
]
