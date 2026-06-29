from __future__ import annotations

from pk_radar.mcp.tool_schema import MCPTool, MCPToolSpec


class MCPToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPTool] = {}
        self._aliases: dict[str, str] = {}

    def register(self, tool: MCPTool) -> None:
        self._tools[tool.spec.name] = tool
        for alias in tool.spec.aliases:
            self._aliases[alias] = tool.spec.name

    def resolve(self, name: str) -> MCPTool:
        canonical = self._aliases.get(name, name)
        if canonical not in self._tools:
            raise KeyError(f"MCP tool not found: {name}")
        return self._tools[canonical]

    def list_specs(self) -> list[MCPToolSpec]:
        return [tool.spec for tool in self._tools.values()]