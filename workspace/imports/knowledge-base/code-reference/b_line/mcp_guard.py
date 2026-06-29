"""B-Line MCP Guard - Tool permission control for agent MCP calls.

Manages tool whitelists per role, enforces rate limits (token bucket),
and maintains an audit log of all access attempts.
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Any
import json
import hashlib


class MCPGuard:
    """Gatekeeper for MCP tool access by agent roles.

    Features:
    - Tool whitelist per role with allow/deny
    - Rate limiting (per-minute and per-hour)
    - Concurrency limits
    - Approval requirements for sensitive tools
    - Full audit logging
    """

    def __init__(self, store: Any) -> None:
        self._store = store

    # ── Permission Rules ──

    def set_permission(self, role_name: str, tool_name: str,
                       allowed: bool = True, rate_limit_per_min: int = 60,
                       rate_limit_per_hour: int = 1000, max_concurrent: int = 5,
                       require_approval: bool = False) -> bool:
        ts = datetime.now(timezone.utc).isoformat()
        existing = self._store.conn.execute(
            "SELECT id FROM mcp_permissions WHERE role_name=? AND tool_name=?",
            (role_name, tool_name)).fetchone()
        if existing:
            self._store.conn.execute(
                "UPDATE mcp_permissions SET allowed=?, rate_limit_per_min=?,"
                " rate_limit_per_hour=?, max_concurrent=?, require_approval=?,"
                " updated_at=? WHERE id=?",
                (1 if allowed else 0, rate_limit_per_min, rate_limit_per_hour,
                 max_concurrent, 1 if require_approval else 0, ts, existing[0]))
        else:
            self._store.conn.execute(
                "INSERT INTO mcp_permissions (role_name, tool_name, allowed,"
                " rate_limit_per_min, rate_limit_per_hour, max_concurrent,"
                " require_approval, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (role_name, tool_name, 1 if allowed else 0, rate_limit_per_min,
                 rate_limit_per_hour, max_concurrent, 1 if require_approval else 0, ts, ts))
        self._store.conn.commit()
        return True

    def get_permission(self, role_name: str, tool_name: str) -> dict | None:
        row = self._store.conn.execute(
            "SELECT * FROM mcp_permissions WHERE role_name=? AND tool_name=?",
            (role_name, tool_name)).fetchone()
        return dict(row) if row else None

    def list_permissions(self, role_name: str = "") -> list[dict]:
        if role_name:
            cur = self._store.conn.execute(
                "SELECT * FROM mcp_permissions WHERE role_name=? ORDER BY tool_name",
                (role_name,))
        else:
            cur = self._store.conn.execute(
                "SELECT * FROM mcp_permissions ORDER BY role_name, tool_name")
        return [dict(r) for r in cur.fetchall()]

    def delete_permission(self, role_name: str, tool_name: str) -> bool:
        self._store.conn.execute(
            "DELETE FROM mcp_permissions WHERE role_name=? AND tool_name=?",
            (role_name, tool_name))
        self._store.conn.commit()
        return True

    # ── Access Check ──

    def check_access(self, role_name: str, tool_name: str,
                     params: dict | None = None, ip_address: str = "") -> dict:
        """Check if a role is allowed to call a tool. Returns a decision dict."""
        perm = self.get_permission(role_name, tool_name)

        if not perm or not perm.get("allowed"):
            self._log_audit(role_name, tool_name, "call", False, "not_allowed",
                            params, ip_address)
            return {"allowed": False, "reason": "not_allowed"}

        # Check rate limits
        rate_ok, rate_reason = self._check_rate_limit(
            role_name, tool_name,
            perm.get("rate_limit_per_min", 60),
            perm.get("rate_limit_per_hour", 1000))
        if not rate_ok:
            self._log_audit(role_name, tool_name, "call", False, rate_reason,
                            params, ip_address)
            return {"allowed": False, "reason": rate_reason}

        # Check concurrency
        conc_ok, conc_reason = self._check_concurrency(
            role_name, tool_name,
            perm.get("max_concurrent", 5))
        if not conc_ok:
            self._log_audit(role_name, tool_name, "call", False, conc_reason,
                            params, ip_address)
            return {"allowed": False, "reason": conc_reason}

        # Approval required?
        if perm.get("require_approval"):
            self._log_audit(role_name, tool_name, "call", True, "approval_required",
                            params, ip_address)
            return {"allowed": True, "requires_approval": True,
                    "reason": "approval_required"}

        self._log_audit(role_name, tool_name, "call", True, "allowed",
                        params, ip_address)
        return {"allowed": True, "reason": "allowed"}

    # ── Rate Limiting (Token Bucket) ──

    def _check_rate_limit(self, role_name: str, tool_name: str,
                          per_min: int, per_hour: int) -> tuple[bool, str]:
        now = datetime.now(timezone.utc)
        minute_start = now.replace(second=0, microsecond=0).isoformat()
        hour_start = now.replace(minute=0, second=0, microsecond=0).isoformat()

        # Check per-minute
        min_count = self._store.conn.execute(
            "SELECT SUM(call_count) FROM mcp_rate_buckets WHERE role_name=? AND"
            " tool_name=? AND window_start >= ?",
            (role_name, tool_name, minute_start)).fetchone()[0] or 0
        if min_count >= per_min:
            return False, "rate_limit_per_min_exceeded"

        # Check per-hour
        hour_count = self._store.conn.execute(
            "SELECT SUM(call_count) FROM mcp_rate_buckets WHERE role_name=? AND"
            " tool_name=? AND window_start >= ?",
            (role_name, tool_name, hour_start)).fetchone()[0] or 0
        if hour_count >= per_hour:
            return False, "rate_limit_per_hour_exceeded"

        # Record this call
        existing = self._store.conn.execute(
            "SELECT id, call_count FROM mcp_rate_buckets WHERE role_name=? AND"
            " tool_name=? AND window_start=?",
            (role_name, tool_name, minute_start)).fetchone()
        if existing:
            self._store.conn.execute(
                "UPDATE mcp_rate_buckets SET call_count=? WHERE id=?",
                (existing[1] + 1, existing[0]))
        else:
            self._store.conn.execute(
                "INSERT INTO mcp_rate_buckets (role_name, tool_name, window_start, call_count)"
                " VALUES (?, ?, ?, 1)",
                (role_name, tool_name, minute_start))
        self._store.conn.commit()
        return True, "ok"

    def _check_concurrency(self, role_name: str, tool_name: str,
                           max_concurrent: int) -> tuple[bool, str]:
        # Count recent in-flight calls (last 30 seconds without completion)
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat()
        count = self._store.conn.execute(
            "SELECT COUNT(*) FROM mcp_audit_log WHERE role_name=? AND tool_name=?"
            " AND action='call' AND created_at >= ?",
            (role_name, tool_name, cutoff)).fetchone()[0] or 0
        if count >= max_concurrent:
            return False, "concurrency_limit_exceeded"
        return True, "ok"

    # ── Audit Log ──

    def _log_audit(self, role_name: str, tool_name: str, action: str,
                   allowed: bool, reason: str, params: dict | None,
                   ip_address: str) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        params_hash = ""
        if params:
            raw = json.dumps(params, sort_keys=True, default=str)
            params_hash = hashlib.md5(raw.encode()).hexdigest()[:12]
        self._store.conn.execute(
            "INSERT INTO mcp_audit_log (role_name, tool_name, action, allowed,"
            " reason, request_params_hash, ip_address, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (role_name, tool_name, action, 1 if allowed else 0, reason,
             params_hash, ip_address, ts))
        self._store.conn.commit()

    def get_audit_log(self, role_name: str = "", tool_name: str = "",
                      limit: int = 50, allowed_only: bool | None = None) -> list[dict]:
        conditions = []
        params = []
        if role_name:
            conditions.append("role_name=?")
            params.append(role_name)
        if tool_name:
            conditions.append("tool_name=?")
            params.append(tool_name)
        if allowed_only is not None:
            conditions.append("allowed=?")
            params.append(1 if allowed_only else 0)

        where = " AND ".join(conditions) if conditions else "1=1"
        cur = self._store.conn.execute(
            f"SELECT * FROM mcp_audit_log WHERE {where} ORDER BY created_at DESC LIMIT ?",
            params + [limit])
        return [dict(r) for r in cur.fetchall()]

    def get_audit_summary(self, hours: int = 24) -> dict:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        total = self._store.conn.execute(
            "SELECT COUNT(*) FROM mcp_audit_log WHERE created_at >= ?",
            (cutoff,)).fetchone()[0] or 0
        allowed = self._store.conn.execute(
            "SELECT COUNT(*) FROM mcp_audit_log WHERE created_at >= ? AND allowed=1",
            (cutoff,)).fetchone()[0] or 0
        denied = total - allowed

        # Top tools by call count
        top_tools = self._store.conn.execute(
            "SELECT tool_name, COUNT(*) as cnt FROM mcp_audit_log"
            " WHERE created_at >= ? GROUP BY tool_name ORDER BY cnt DESC LIMIT 10",
            (cutoff,)).fetchall()

        # Top denied roles
        top_denied = self._store.conn.execute(
            "SELECT role_name, COUNT(*) as cnt FROM mcp_audit_log"
            " WHERE created_at >= ? AND allowed=0 GROUP BY role_name"
            " ORDER BY cnt DESC LIMIT 5",
            (cutoff,)).fetchall()

        return {
            "period_hours": hours,
            "total_calls": total,
            "allowed": allowed,
            "denied": denied,
            "allow_rate": round(allowed / max(total, 1), 3),
            "top_tools": [{"tool": r[0], "count": r[1]} for r in top_tools],
            "top_denied_roles": [{"role": r[0], "count": r[1]} for r in top_denied],
        }

    # ── Rate Limit Stats ──

    def get_rate_limit_status(self, role_name: str = "") -> dict:
        if role_name:
            cur = self._store.conn.execute(
                "SELECT tool_name, SUM(call_count) as total FROM mcp_rate_buckets"
                " WHERE role_name=? GROUP BY tool_name ORDER BY total DESC",
                (role_name,))
        else:
            cur = self._store.conn.execute(
                "SELECT role_name, tool_name, SUM(call_count) as total"
                " FROM mcp_rate_buckets GROUP BY role_name, tool_name"
                " ORDER BY total DESC LIMIT 20")
        return {
            "buckets": [
                {"role": r[0], "tool": r[1], "call_count": r[2]}
                if len(r) == 3 else
                {"tool": r[0], "call_count": r[1]}
                for r in cur.fetchall()
            ]
        }

    # ── Cleanup ──

    def cleanup_old_audit_logs(self, days: int = 30) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        cur = self._store.conn.execute(
            "DELETE FROM mcp_audit_log WHERE created_at < ?", (cutoff,))
        self._store.conn.commit()
        return cur.rowcount

    def cleanup_old_rate_buckets(self, hours: int = 2) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        cur = self._store.conn.execute(
            "DELETE FROM mcp_rate_buckets WHERE window_start < ?", (cutoff,))
        self._store.conn.commit()
        return cur.rowcount


__all__ = ["MCPGuard"]
