"""MCP Engine - with plugin loader"""

from __future__ import annotations


class MCPPlugin:
    def __init__(self, name, version="1.0.0", command=None, args=None):
        self.name = name
        self.version = version
        self.command = command
        self.args = args or []
        self.status = "inactive"


class MCPEngine:
    def __init__(self, store=None):
        self._store = store
        self._plugins = {}
        self._handlers = {}

    def register_tool(self, name, handler):
        self._handlers[name] = handler

    def register_plugin(self, name, cmd):
        self._plugins[name] = MCPPlugin(name, command=cmd)

    def call(self, name, params):
        h = self._handlers.get(name)
        return h(params) if h else {"error": f"tool not found: {name}"}

    def list_tools(self):
        return list(self._handlers.keys())

    def list_plugins(self):
        return [
            {"name": p.name, "version": p.version, "status": p.status}
            for p in self._plugins.values()
        ]
