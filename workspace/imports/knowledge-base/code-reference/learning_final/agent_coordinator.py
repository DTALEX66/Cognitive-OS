"""Agent Coordinator - with spawn utils + mailbox"""

from __future__ import annotations
from enum import Enum
import uuid
import time
import threading


class AgentRole(Enum):
    RESEARCH = "research"
    ANALYZE = "analyze"
    CREATE = "create"
    REVIEW = "review"
    TEST = "test"
    DEBUG = "debug"
    COORDINATE = "coordinate"
    EXECUTE = "execute"


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


class AgentCoordinator:
    def __init__(self, store=None):
        self._store = store
        self._agents = {}
        self._memories = {}
        self._lock = threading.Lock()

    def dispatch(self, role, prompt, context=None, parent_id=None):
        agent_id = role.value + "_" + uuid.uuid4().hex[:8]
        with self._lock:
            self._agents[agent_id] = {
                "id": agent_id,
                "role": role.value,
                "status": AgentStatus.RUNNING.value,
                "prompt": prompt,
                "context": context or {},
                "parent_id": parent_id,
                "created_at": time.time(),
            }
        return {"agent_id": agent_id, "role": role.value, "status": "dispatched"}

    def save_memory(self, task_id, key, value):
        with self._lock:
            if task_id not in self._memories:
                self._memories[task_id] = {}
            self._memories[task_id][key] = value

    def recall_memory(self, task_id, key):
        return self._memories.get(task_id, {}).get(key)

    def list_active(self):
        with self._lock:
            return [a for a in self._agents.values() if a["status"] == "running"]

    def swarm_create(self, name, mode="sequential"):
        return uuid.uuid4().hex[:8]

    def swarm_add_agent(self, team_id, role="worker"):
        return self.dispatch(AgentRole.EXECUTE, "Swarm agent for " + team_id)

    def swarm_run(self, team_id, objective):
        return [{"team": team_id, "objective": objective, "status": "running"}]

    def agent_fork(self, task_id, prompt):
        return self.dispatch(AgentRole.EXECUTE, prompt, parent_id=task_id)
