"""Task Engine - with dependency graph, priority, retry, timeout"""

from __future__ import annotations
from enum import Enum
import threading
import uuid
import heapq
from datetime import datetime, timezone


class TaskPriority(Enum):
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class Task:
    def __init__(
        self,
        name,
        fn=None,
        priority=TaskPriority.NORMAL,
        timeout_s=300,
        max_retries=3,
        depends_on=None,
    ):
        self.id = uuid.uuid4().hex[:12]
        self.name = name
        self.fn = fn
        self.priority = priority
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.retries = 0
        self.depends_on = depends_on or []
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.result = None
        self.error = None

    def can_run(self, completed_ids):
        return all(d in completed_ids for d in self.depends_on)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority.value,
        }


class TaskEngine:
    def __init__(self, store=None):
        self._tasks = {}
        self._queue = []
        self._counter = 0
        self._lock = threading.Lock()
        self._completed = set()

    def create(
        self,
        name,
        fn=None,
        priority=TaskPriority.NORMAL,
        timeout_s=300,
        max_retries=3,
        depends_on=None,
    ):
        with self._lock:
            task = Task(name, fn, priority, timeout_s, max_retries, depends_on)
            self._tasks[task.id] = task
            heapq.heappush(self._queue, (task.priority.value, self._counter, task.id))
            self._counter += 1
            return task.id

    def get(self, tid):
        task = self._tasks.get(tid)
        return task.to_dict() if task else None

    def list(self, status=None, limit=50):
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status.value == status]
        return [t.to_dict() for t in tasks[:limit]]

    def cancel(self, tid):
        task = self._tasks.get(tid)
        if task and task.status in (TaskStatus.PENDING, TaskStatus.BLOCKED):
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def count_by_status(self):
        counts = {}
        for t in self._tasks.values():
            s = t.status.value
            counts[s] = counts.get(s, 0) + 1
        return counts
