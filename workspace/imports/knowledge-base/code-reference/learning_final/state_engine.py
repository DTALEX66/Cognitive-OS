"""State Engine - persistent app state"""

from __future__ import annotations
import threading


class AppState:
    def __init__(self):
        self._data = {"mode": "learning", "session_count": 0}
        self._lock = threading.Lock()

    def get(self, k, d=None):
        with self._lock:
            return self._data.get(k, d)

    def set(self, k, v):
        with self._lock:
            self._data[k] = v

    def snapshot(self):
        with self._lock:
            return dict(self._data)


class StateEngine:
    def __init__(self, store=None):
        self._store = store
        self._state = AppState()

    def get(self, k, d=None):
        return self._state.get(k, d)

    def set(self, k, v):
        self._state.set(k, v)

    def snapshot(self):
        return self._state.snapshot()
