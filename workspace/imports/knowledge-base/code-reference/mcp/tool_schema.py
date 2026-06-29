from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class MCPToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    permission: str
    side_effect: bool = False
    risk_level: str = "low"
    aliases: list[str] = field(default_factory=list)


@dataclass
class MCPTool:
    spec: MCPToolSpec
    handler: Callable[[dict[str, Any]], Any]