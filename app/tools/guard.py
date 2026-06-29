from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ToolGuardDecision:
    allowed: bool
    effective_dry_run: bool
    reasons: list[str] = field(default_factory=list)
    status: str = 'ok'

    def as_metadata(self) -> dict[str, Any]:
        return {
            'allowed': self.allowed,
            'effective_dry_run': self.effective_dry_run,
            'reasons': self.reasons,
        }


def _resolve_inside(base: Path, path_value: str) -> Path | None:
    try:
        candidate = Path(str(path_value))
        target = candidate if candidate.is_absolute() else base / candidate
        resolved = target.resolve()
        resolved.relative_to(base.resolve())
        return resolved
    except Exception:
        return None


def _effective_dry_run(default_dry_run: bool, requested_dry_run: bool | None) -> tuple[bool, list[str]]:
    if requested_dry_run is None:
        return bool(default_dry_run), ['default_dry_run_applied']
    return bool(requested_dry_run), [f'explicit_dry_run={bool(requested_dry_run)}']


def guard_tool_request(
    spec: Any,
    payload: dict[str, Any],
    requested_dry_run: bool | None,
    *,
    project_root: Path,
    safe_output_dir: Path,
) -> ToolGuardDecision:
    risk_level = str(getattr(spec, 'risk_level', 'unknown'))
    tool_name = str(getattr(spec, 'name', 'unknown'))
    default_dry_run = bool(getattr(spec, 'default_dry_run', True))
    effective_dry_run, reasons = _effective_dry_run(default_dry_run, requested_dry_run)

    reasons.extend([f'tool={tool_name}', f'risk={risk_level}'])

    if risk_level == 'high':
        return ToolGuardDecision(
            allowed=False,
            effective_dry_run=True,
            reasons=[*reasons, 'high_risk_tool_blocked', 'manual_review_required'],
            status='blocked',
        )

    if risk_level == 'medium':
        if effective_dry_run:
            reasons.append('medium_risk_dry_run')
        else:
            reasons.append('medium_risk_explicit_execution_requested')

    if tool_name == 'file_read':
        path_value = str(payload.get('path', ''))
        if not path_value.strip():
            return ToolGuardDecision(
                allowed=False,
                effective_dry_run=effective_dry_run,
                reasons=[*reasons, 'path_required'],
                status='blocked',
            )
        if _resolve_inside(project_root, path_value) is None:
            return ToolGuardDecision(
                allowed=False,
                effective_dry_run=effective_dry_run,
                reasons=[*reasons, 'path_must_stay_inside_project_root'],
                status='blocked',
            )

    if tool_name == 'safe_write':
        filename = str(payload.get('filename', 'output.txt'))
        if not filename.strip():
            return ToolGuardDecision(
                allowed=False,
                effective_dry_run=effective_dry_run,
                reasons=[*reasons, 'filename_required'],
                status='blocked',
            )
        if Path(filename).is_absolute() or '..' in Path(filename).parts:
            return ToolGuardDecision(
                allowed=False,
                effective_dry_run=effective_dry_run,
                reasons=[*reasons, 'safe_write_target_must_stay_under_data_output'],
                status='blocked',
            )
        if _resolve_inside(safe_output_dir, filename) is None:
            return ToolGuardDecision(
                allowed=False,
                effective_dry_run=effective_dry_run,
                reasons=[*reasons, 'safe_write_target_must_stay_under_data_output'],
                status='blocked',
            )

    return ToolGuardDecision(
        allowed=True,
        effective_dry_run=effective_dry_run,
        reasons=[*reasons, 'allowed'],
    )
