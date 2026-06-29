"""B-Line Agent Role - Role assignment engine with permission matrix.

Defines agent roles, their capabilities, permission matrices,
and task assignment logic.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json


DEFAULT_ROLES = {
    "planner": {
        "role_type": "orchestrator",
        "description": "Task decomposition and route planning agent",
        "capabilities": ["task_decomposition", "route_planning", "dependency_analysis"],
        "permission_matrix": {"decompose_task": 1, "create_route": 1, "list_routes": 1, "update_state": 1},
        "priority": 1, "max_concurrent_tasks": 3, "rate_limit_per_min": 30,
    },
    "researcher": {
        "role_type": "worker",
        "description": "Knowledge retrieval and context assembly agent",
        "capabilities": ["knowledge_retrieval", "context_assembly", "semantic_search"],
        "permission_matrix": {"search_knowledge": 1, "get_knowledge": 1, "build_context": 1, "read_file": 1},
        "priority": 2, "max_concurrent_tasks": 5, "rate_limit_per_min": 60,
    },
    "coder": {
        "role_type": "worker",
        "description": "Code generation and patch creation agent",
        "capabilities": ["code_generation", "patch_creation", "file_editing", "refactoring"],
        "permission_matrix": {"generate_code": 1, "apply_patch": 1, "write_file": 1, "read_file": 1, "execute_command": 1},
        "priority": 3, "max_concurrent_tasks": 3, "rate_limit_per_min": 45,
    },
    "tester": {
        "role_type": "worker",
        "description": "Test generation and validation agent",
        "capabilities": ["test_generation", "validation", "coverage_analysis"],
        "permission_matrix": {"run_tests": 1, "generate_tests": 1, "read_file": 1, "execute_command": 1},
        "priority": 4, "max_concurrent_tasks": 3, "rate_limit_per_min": 45,
    },
    "reviewer": {
        "role_type": "reviewer",
        "description": "Code review and quality check agent",
        "capabilities": ["code_review", "quality_check", "style_enforcement"],
        "permission_matrix": {"review_code": 1, "read_file": 1, "get_diagnostics": 1},
        "priority": 5, "max_concurrent_tasks": 2, "rate_limit_per_min": 30,
    },
    "security": {
        "role_type": "guard",
        "description": "Security audit and permission check agent",
        "capabilities": ["security_audit", "permission_check", "vulnerability_scan"],
        "permission_matrix": {"audit_security": 1, "check_permissions": 1, "read_file": 1, "block_tool": 1},
        "priority": 6, "max_concurrent_tasks": 2, "rate_limit_per_min": 20,
    },
    "memory_curator": {
        "role_type": "worker",
        "description": "Experience tracking and lesson extraction agent",
        "capabilities": ["experience_tracking", "lesson_extraction", "pattern_recognition"],
        "permission_matrix": {"write_memory": 1, "read_memory": 1, "extract_lesson": 1, "update_route": 1},
        "priority": 7, "max_concurrent_tasks": 2, "rate_limit_per_min": 20,
    },
}


class AgentRoleEngine:
    def __init__(self, store: Any) -> None:
        self._store = store
        self._ensure_default_roles()

    def _ensure_default_roles(self) -> None:
        existing = {r["name"] for r in self.list_roles()}
        ts = datetime.now(timezone.utc).isoformat()
        for name, cfg in DEFAULT_ROLES.items():
            if name not in existing:
                self._store.conn.execute(
                    "INSERT INTO agent_roles (name, role_type, description, capabilities,"
                    " permission_matrix, priority, max_concurrent_tasks, rate_limit_per_min,"
                    " enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)",
                    (name, cfg["role_type"], cfg["description"],
                     json.dumps(cfg["capabilities"]),
                     json.dumps(cfg["permission_matrix"]),
                     cfg["priority"], cfg["max_concurrent_tasks"],
                     cfg["rate_limit_per_min"], ts))
        self._store.conn.commit()

    def create_role(self, name, role_type="worker", description="",
                    capabilities=None, permissions=None,
                    priority=5, max_concurrent=5, rate_limit=60):
        ts = datetime.now(timezone.utc).isoformat()
        caps = json.dumps(capabilities or [])
        perms = json.dumps(permissions or {})
        cur = self._store.conn.execute(
            "INSERT INTO agent_roles (name, role_type, description, capabilities,"
            " permission_matrix, priority, max_concurrent_tasks, rate_limit_per_min,"
            " enabled, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?)",
            (name, role_type, description, caps, perms, priority,
             max_concurrent, rate_limit, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def get_role(self, role_id):
        row = self._store.conn.execute(
            "SELECT * FROM agent_roles WHERE id=?", (role_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        r["capabilities"] = json.loads(r.get("capabilities", "[]"))
        r["permission_matrix"] = json.loads(r.get("permission_matrix", "{}"))
        return r

    def get_role_by_name(self, name):
        row = self._store.conn.execute(
            "SELECT * FROM agent_roles WHERE name=?", (name,)).fetchone()
        if not row:
            return None
        r = dict(row)
        r["capabilities"] = json.loads(r.get("capabilities", "[]"))
        r["permission_matrix"] = json.loads(r.get("permission_matrix", "{}"))
        return r

    def update_role(self, role_id, **kwargs):
        existing = self.get_role(role_id)
        if not existing:
            return False
        updates = {}
        field_map = {
            "name": "name", "role_type": "role_type",
            "description": "description", "priority": "priority",
            "max_concurrent": "max_concurrent_tasks",
            "rate_limit": "rate_limit_per_min", "enabled": "enabled",
        }
        for kw, col in field_map.items():
            if kw in kwargs and kwargs[kw] is not None:
                updates[col] = kwargs[kw]
        if "capabilities" in kwargs:
            updates["capabilities"] = json.dumps(kwargs["capabilities"])
        if "permissions" in kwargs:
            updates["permission_matrix"] = json.dumps(kwargs["permissions"])
        if not updates:
            return True
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [role_id]
        self._store.conn.execute(f"UPDATE agent_roles SET {set_clause} WHERE id=?", values)
        self._store.conn.commit()
        return True

    def delete_role(self, role_id):
        existing = self.get_role(role_id)
        if not existing:
            return False
        self._store.conn.execute("DELETE FROM agent_roles WHERE id=?", (role_id,))
        self._store.conn.commit()
        return True

    def list_roles(self, enabled_only=False):
        if enabled_only:
            cur = self._store.conn.execute(
                "SELECT * FROM agent_roles WHERE enabled=1 ORDER BY priority")
        else:
            cur = self._store.conn.execute(
                "SELECT * FROM agent_roles ORDER BY priority")
        result = []
        for row in cur.fetchall():
            r = dict(row)
            r["capabilities"] = json.loads(r.get("capabilities", "[]"))
            r["permission_matrix"] = json.loads(r.get("permission_matrix", "{}"))
            result.append(r)
        return result

    def can_use_tool(self, role_name, tool_name):
        role = self.get_role_by_name(role_name)
        if not role or not role.get("enabled"):
            return False
        return role.get("permission_matrix", {}).get(tool_name, 0) == 1

    def get_tool_permissions(self, role_name):
        role = self.get_role_by_name(role_name)
        if not role:
            return {}
        return role.get("permission_matrix", {})

    def grant_permission(self, role_id, tool_name):
        role = self.get_role(role_id)
        if not role:
            return False
        perms = role.get("permission_matrix", {})
        perms[tool_name] = 1
        return self.update_role(role_id, permissions=perms)

    def revoke_permission(self, role_id, tool_name):
        role = self.get_role(role_id)
        if not role:
            return False
        perms = role.get("permission_matrix", {})
        perms[tool_name] = 0
        return self.update_role(role_id, permissions=perms)

    def add_capability(self, role_id, capability):
        role = self.get_role(role_id)
        if not role:
            return False
        caps = role.get("capabilities", [])
        if capability not in caps:
            caps.append(capability)
            return self.update_role(role_id, capabilities=caps)
        return True

    def remove_capability(self, role_id, capability):
        role = self.get_role(role_id)
        if not role:
            return False
        caps = role.get("capabilities", [])
        if capability in caps:
            caps.remove(capability)
            return self.update_role(role_id, capabilities=caps)
        return True

    def has_capability(self, role_name, capability):
        role = self.get_role_by_name(role_name)
        if not role:
            return False
        return capability in role.get("capabilities", [])

    def assign_for_task(self, goal, required_capabilities=None):
        roles = self.list_roles(enabled_only=True)
        if not required_capabilities:
            return [{
                "role": r["name"], "role_type": r["role_type"],
                "capabilities": r["capabilities"],
                "permissions": r["permission_matrix"],
                "priority": r["priority"],
            } for r in roles]
        scored = []
        goal_lower = goal.lower()
        for r in roles:
            caps = r.get("capabilities", [])
            match_count = sum(1 for c in required_capabilities if c in caps)
            if match_count == 0:
                continue
            desc_bonus = 0
            for word in r.get("description", "").lower().split():
                if len(word) > 2 and word in goal_lower:
                    desc_bonus += 0.5
            score = match_count * 10 + desc_bonus + (10 - r["priority"]) * 2
            scored.append((score, {
                "role": r["name"], "role_type": r["role_type"],
                "capabilities": caps,
                "permissions": r.get("permission_matrix", {}),
                "priority": r["priority"],
                "match_count": match_count, "score": round(score, 2),
            }))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored]

    def get_best_role(self, goal, required_capabilities=None):
        assignments = self.assign_for_task(goal, required_capabilities)
        return assignments[0] if assignments else None

    def export_permission_matrix(self):
        roles = self.list_roles()
        all_tools = set()
        for r in roles:
            all_tools.update(r.get("permission_matrix", {}).keys())
        tools_sorted = sorted(all_tools)
        matrix = {"tools": tools_sorted, "roles": {}}
        for r in roles:
            perms = r.get("permission_matrix", {})
            matrix["roles"][r["name"]] = {
                "role_type": r["role_type"], "priority": r["priority"],
                "permissions": {t: perms.get(t, 0) for t in tools_sorted},
                "capabilities": r.get("capabilities", []),
            }
        return matrix

    def export_capability_matrix(self):
        roles = self.list_roles()
        all_caps = set()
        for r in roles:
            all_caps.update(r.get("capabilities", []))
        caps_sorted = sorted(all_caps)
        matrix = {}
        for r in roles:
            rcaps = r.get("capabilities", [])
            matrix[r["name"]] = {
                "role_type": r["role_type"],
                "capabilities": {c: (c in rcaps) for c in caps_sorted},
            }
        return {"capabilities": caps_sorted, "roles": matrix}


__all__ = ["DEFAULT_ROLES", "AgentRoleEngine"]
