"""安全策略：配置安全等级与验证规则，支持责任披露。"""

from __future__ import annotations

import re
from typing import Any


class SafetyPolicy:
    def __init__(self, level: str = "default", stop_on_blocked: bool = True, confirm_personal_right: bool = False, **kwargs):
        self.level = level
        self.stop_on_blocked = stop_on_blocked
        self.confirm_personal_right = confirm_personal_right
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.stop_on_blocked = stop_on_blocked
        self.confirm_personal_right = confirm_personal_right

    def to_dict(self) -> dict[str, Any]:
        return {"level": self.level}


def validate_capability_profile(p: Any) -> bool:
    return True


def validate_mode(m: str, policy: SafetyPolicy | None = None) -> bool:
    if m == "stealthy" and policy and policy.level != "admin":
        raise ValueError("Stealthy mode requires admin-level policy")
    return True


def validate_url_for_ingest(u: str, policy: SafetyPolicy | None = None) -> bool:
    if not u.startswith(("http://", "https://")):
        raise ValueError(f"URL must start with http:// or https://, got: {u}")
    return True


def should_stop_on_status(s: int, response: Any = None) -> bool:
    """Returns True if status code >= 400 (client/server error)."""
    return s >= 400


def validate_stealthy_confirmation(
    confirmed: bool,
    user_controlled: bool,
    require_confirmation: bool = False,
) -> bool:
    """Validate stealth mode confirmation.

    Args:
        confirmed: Whether the user confirmed.
        user_controlled: Whether the user controls the setting.
        require_confirmation: If True, requires explicit confirmation.
    """
    if require_confirmation and not user_controlled:
        raise ValueError("Stealth mode requires user-controlled setting when hard-gated")
    if require_confirmation and not confirmed:
        raise ValueError("Stealth mode requires explicit confirmation")
    return confirmed and (user_controlled or require_confirmation)


def redact_sensitive_text(text: str, policy: SafetyPolicy | None = None) -> str:
    """Redact sensitive patterns (API keys, tokens, emails, SSN, phone) from text."""
    patterns = [
        (r"[A-Za-z0-9_-]{20,}", "<REDACTED_KEY>"),
        (r"[\w.+-]+@[\w-]+\.[\w.-]+", "<REDACTED_EMAIL>"),
        (r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+", r"\1: <REDACTED>"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "<REDACTED_SSN>"),
        (r"\b1\d{10}\b", "<REDACTED_PHONE>"),
        (r"\b\d{11,}\b", "<REDACTED_NUMBER>"),
    ]
    result = text
    for pat, repl in patterns:
        result = re.sub(pat, repl, result)
    return result


def stealthy_usage_notice() -> str:
    return (
        "WARNING: Stealth mode active. This tool bypasses certain website protections. "
        "Use only on systems you own or have explicit permission to test."
    )


def capability_profile_notice() -> str:
    return (
        "This agent operates with full capability profile. "
        "All actions are logged for audit purposes."
    )

