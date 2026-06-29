'''Tool Pool - mode-aware tool management from CW tool_pool.py'''
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PoolItem:
    name: str
    category: str
    enabled: bool = True

class ToolPool:
    def __init__(self):
        self._items = {}
        self.simple_mode = False
        self.include_mcp = False
    def add(self, name, category='builtin'):
        self._items[name] = PoolItem(name, category)
    def enable(self, name):
        if name in self._items: self._items[name].enabled = True
    def disable(self, name):
        if name in self._items: self._items[name].enabled = False
    def active(self):
        v = self._items.values()
        if self.simple_mode: v = [x for x in v if x.category == 'builtin']
        return [x.name for x in v if x.enabled]
    def set_mode(self, simple=False, mcp=False):
        self.simple_mode = simple; self.include_mcp = mcp
