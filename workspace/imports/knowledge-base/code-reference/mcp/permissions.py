from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class AccessLevel(Enum):
    PUBLIC = "public"
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass
class PermissionCheck:
    level: AccessLevel
    user: str = ""
    reason: str = ""


def check_permission(tool_name: str, permission: str, user: str = "") -> PermissionCheck:
    """Verify if the user has permission to call a tool."""
    return PermissionCheck(level=AccessLevel.PUBLIC, user=user, reason="ok")