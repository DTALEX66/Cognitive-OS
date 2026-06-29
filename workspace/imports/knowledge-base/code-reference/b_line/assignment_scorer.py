"""Assignment scorer: matches tasks to the best-fit agent role"""
import json
import os
from typing import List, Dict, Optional


class AssignmentScorer:
    def __init__(self, store=None):
        self._store = store
        self._roles = self._load_roles()

    def _load_roles(self):
        idx_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "agents", "role_index.json")
        if not os.path.exists(idx_path):
            return []
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        return idx.get("roles", [])

    def score_role(self, task_type, required_capabilities, role):
        if not isinstance(role, dict):
            return 0.0
        score = 0.0
        role_caps = set(role.get("capabilities", []))
        req_caps = set(required_capabilities)
        if req_caps:
            overlap = req_caps & role_caps
            score += len(overlap) / len(req_caps) * 60.0
        if task_type in role.get("triggers", []):
            score += 20.0
        priority = role.get("priority", 10)
        score += max(0, 10 - priority) * 2.0
        return min(100.0, score)

    def best_role(self, task_type, required_capabilities=None):
        if not self._roles:
            return None
        caps = required_capabilities or []
        scored = [(r, self.score_role(task_type, caps, r)) for r in self._roles]
        scored.sort(key=lambda x: -x[1])
        return scored[0][0] if scored[0][1] > 0 else None

    def assign_agents(self, task_type, required_capabilities, count=1):
        if not self._roles:
            return []
        scored = [(r, self.score_role(task_type, required_capabilities, r)) for r in self._roles]
        scored.sort(key=lambda x: -x[1])
        return [r for r, s in scored[:count] if s > 0]

    def list_capabilities(self):
        return {r["role"]: r.get("capabilities", []) for r in self._roles}

    def needs_role(self, role_name):
        for r in self._roles:
            if r["role"] == role_name:
                return r
        return None
