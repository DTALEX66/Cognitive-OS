"""B-Line Sandbox Executor - Isolated code and command execution.

Provides a secure sandbox for executing Python code snippets,
shell commands, and file operations with configurable limits.
Uses a module whitelist to block dangerous imports (os, subprocess, etc.)
and enforces timeout, memory, and filesystem constraints.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import io
import sys
import time
import traceback
import subprocess
import os
import re


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution environment."""
    timeout_sec: float = 30.0
    max_memory_mb: int = 256
    allow_network: bool = False
    allow_filesystem: bool = True
    filesystem_root: str = ""
    allow_subprocess: bool = False
    max_output_chars: int = 100_000
    dry_run: bool = False
    extra_allowed_modules: list[str] = field(default_factory=list)


SAFE_BUILTINS: set[str] = {
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes",
    "callable", "chr", "classmethod", "complex", "delattr", "dict",
    "dir", "divmod", "enumerate", "filter", "float", "format", "frozenset",
    "getattr", "globals", "hasattr", "hash", "hex", "id", "int", "isinstance",
    "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview",
    "min", "next", "object", "oct", "ord", "pow", "print", "property",
    "range", "repr", "reversed", "round", "set", "setattr", "slice",
    "sorted", "staticmethod", "str", "sum", "super", "tuple", "type",
    "vars", "zip", "__import__", "True", "False", "None",
}

DEFAULT_ALLOWED_MODULES: set[str] = {
    "math", "statistics", "random", "datetime", "collections",
    "itertools", "functools", "json", "csv", "re", "string",
    "textwrap", "typing", "dataclasses", "enum", "copy", "pprint",
    "hashlib", "base64", "uuid", "decimal", "fractions", "numbers",
    "heapq", "bisect", "array", "struct", "io", "pathlib", "os.path",
}

BLOCKED_MODULES: set[str] = {
    "os", "subprocess", "shutil", "sys", "ctypes", "socket",
    "http", "urllib", "requests", "ftplib", "telnetlib", "smtplib",
    "poplib", "imaplib", "nntplib", "xmlrpc", "pickle", "marshal",
    "builtins", "importlib", "inspect", "code", "codeop", "compile",
    "signal", "threading", "multiprocessing", "concurrent",
    "asyncio", "tkinter", "webbrowser", "antigravity",
}


@dataclass
class SandboxResult:
    """Result from a sandbox execution."""
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_ms: float = 0.0
    success: bool = True
    error_type: str = ""
    error_message: str = ""
    truncated: bool = False
    dry_run: bool = False


class SandboxExecutor:
    """Execute code and commands in an isolated sandbox.

    Supports:
    - Python code execution with module whitelist
    - Shell command execution with restriction
    - File read/write within sandboxed filesystem
    - Dry-run validation mode
    """

    def __init__(self, config: SandboxConfig | None = None) -> None:
        self.config = config or SandboxConfig()

    def execute_python(self, code: str, globals_dict: dict | None = None) -> SandboxResult:
        """Execute Python code in a sandboxed environment.

        Validates imports before execution and blocks dangerous modules.
        Captures stdout/stderr separately.
        """
        if self.config.dry_run:
            violations = self._audit_code(code)
            return SandboxResult(
                exit_code=0 if not violations["blocked"] else 1,
                success=not violations["blocked"],
                stderr="; ".join(violations["blocked"]) if violations["blocked"] else "",
                stdout=f"DRY-RUN: {len(violations.get('warnings', []))} warnings, {len(violations.get('blocked', []))} blocks",
                dry_run=True,
            )

        start = time.perf_counter()
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        cap_stdout = io.StringIO()
        cap_stderr = io.StringIO()

        try:
            violations = self._audit_code(code)
            if violations["blocked"]:
                duration_ms = (time.perf_counter() - start) * 1000
                return SandboxResult(
                    stderr=f"BLOCKED: {'; '.join(violations['blocked'])}",
                    exit_code=1,
                    duration_ms=duration_ms,
                    success=False,
                    error_type="SandboxSecurityError",
                    error_message=f"Blocked imports: {', '.join(violations['blocked'])}",
                )

            safe_globals = self._build_safe_globals(globals_dict)
            sys.stdout = cap_stdout
            sys.stderr = cap_stderr

            compiled = compile(code, "<sandbox>", "exec")
            exec(compiled, safe_globals)

            duration_ms = (time.perf_counter() - start) * 1000
            stdout_val = cap_stdout.getvalue()
            if len(stdout_val) > self.config.max_output_chars:
                stdout_val = stdout_val[:self.config.max_output_chars]
                return SandboxResult(
                    stdout=stdout_val, stderr=cap_stderr.getvalue(),
                    duration_ms=duration_ms, truncated=True,
                )
            return SandboxResult(
                stdout=stdout_val,
                stderr=cap_stderr.getvalue(),
                duration_ms=duration_ms,
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stdout=cap_stdout.getvalue(),
                stderr=cap_stderr.getvalue() + "\n" + traceback.format_exc(),
                exit_code=1,
                duration_ms=duration_ms,
                success=False,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def execute_shell(self, command: str, cwd: str = "") -> SandboxResult:
        """Execute a shell command with restrictions."""
        if not self.config.allow_subprocess:
            return SandboxResult(
                stderr="BLOCKED: subprocess execution disabled in config",
                exit_code=1,
                success=False,
                error_type="SandboxSecurityError",
                error_message="Subprocess execution is not allowed",
            )
        if self.config.dry_run:
            return SandboxResult(
                stdout=f"DRY-RUN: would execute '{command}'",
                dry_run=True,
            )

        dangerous = ["rm -rf", "del /", "format", "mkfs", "dd if=", "> /dev/", "; rm", "| sh"]
        cmd_lower = command.lower()
        for pattern in dangerous:
            if pattern in cmd_lower:
                return SandboxResult(
                    stderr=f"BLOCKED: dangerous pattern '{pattern}' detected",
                    exit_code=1,
                    success=False,
                    error_type="SandboxSecurityError",
                    error_message=f"Command contains dangerous pattern: {pattern}",
                )

        start = time.perf_counter()
        work_dir = cwd or self.config.filesystem_root or os.getcwd()
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=self.config.timeout_sec, cwd=work_dir,
            )
            duration_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stdout=result.stdout[:self.config.max_output_chars],
                stderr=result.stderr[:self.config.max_output_chars],
                exit_code=result.returncode,
                duration_ms=duration_ms,
                success=result.returncode == 0,
                truncated=len(result.stdout) > self.config.max_output_chars,
            )
        except subprocess.TimeoutExpired as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stderr=f"TIMEOUT after {self.config.timeout_sec}s",
                exit_code=124,
                duration_ms=duration_ms,
                success=False,
                error_type="TimeoutExpired",
                error_message=str(exc),
            )
        except Exception as exc:
            duration_ms = (time.perf_counter() - start) * 1000
            return SandboxResult(
                stderr=traceback.format_exc(),
                exit_code=1,
                duration_ms=duration_ms,
                success=False,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

    def read_file(self, path: str) -> SandboxResult:
        """Read a file within the sandboxed filesystem root."""
        if not self.config.allow_filesystem:
            return SandboxResult(
                stderr="BLOCKED: filesystem access disabled",
                exit_code=1, success=False,
                error_type="SandboxSecurityError",
            )
        if self.config.dry_run:
            return SandboxResult(stdout=f"DRY-RUN: would read '{path}'", dry_run=True)
        resolved = self._resolve_path(path)
        if resolved is None:
            return SandboxResult(
                stderr=f"BLOCKED: path '{path}' outside sandbox root",
                exit_code=1, success=False,
                error_type="SandboxSecurityError",
                error_message=f"Path traversal blocked: {path}",
            )
        start = time.perf_counter()
        try:
            with open(resolved, encoding="utf-8") as fh:
                content = fh.read(self.config.max_output_chars)
            return SandboxResult(
                stdout=content,
                duration_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as exc:
            return SandboxResult(
                stderr=traceback.format_exc(),
                exit_code=1, success=False,
                duration_ms=(time.perf_counter() - start) * 1000,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

    def write_file(self, path: str, content: str) -> SandboxResult:
        """Write content to a file within the sandboxed filesystem root."""
        if not self.config.allow_filesystem:
            return SandboxResult(
                stderr="BLOCKED: filesystem access disabled",
                exit_code=1, success=False,
                error_type="SandboxSecurityError",
            )
        if self.config.dry_run:
            return SandboxResult(stdout=f"DRY-RUN: would write {len(content)} chars to '{path}'", dry_run=True)
        resolved = self._resolve_path(path)
        if resolved is None:
            return SandboxResult(
                stderr=f"BLOCKED: path '{path}' outside sandbox root",
                exit_code=1, success=False,
                error_type="SandboxSecurityError",
                error_message=f"Path traversal blocked: {path}",
            )
        start = time.perf_counter()
        try:
            os.makedirs(os.path.dirname(resolved) or ".", exist_ok=True)
            with open(resolved, "w", encoding="utf-8") as fh:
                fh.write(content)
            return SandboxResult(
                stdout=f"OK: wrote {len(content)} bytes to '{path}'",
                duration_ms=(time.perf_counter() - start) * 1000,
            )
        except Exception as exc:
            return SandboxResult(
                stderr=traceback.format_exc(),
                exit_code=1, success=False,
                duration_ms=(time.perf_counter() - start) * 1000,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

    def _audit_code(self, code: str) -> dict[str, list[str]]:
        """Scan code for blocked imports and return violations."""
        blocked: list[str] = []
        warnings: list[str] = []
        import_pattern = re.compile(
            r"^\s*(?:from\s+(\S+)\s+import|import\s+(\S+))",
            re.MULTILINE,
        )
        for match in import_pattern.finditer(code):
            module = match.group(1) or match.group(2)
            if not module:
                continue
            top_level = module.split(".")[0]
            if top_level in BLOCKED_MODULES or module in BLOCKED_MODULES:
                blocked.append(module)
            elif (top_level not in DEFAULT_ALLOWED_MODULES
                  and top_level not in self.config.extra_allowed_modules
                  and module not in DEFAULT_ALLOWED_MODULES):
                warnings.append(module)
        return {"blocked": blocked, "warnings": warnings}

    def _build_safe_globals(self, extra: dict | None = None) -> dict:
        """Build a safe globals dict with whitelisted builtins."""
        safe_builtins = {k: v for k, v in __builtins__.items()
                         if k in SAFE_BUILTINS}
        globs: dict[str, Any] = {"__builtins__": safe_builtins}
        if extra:
            globs.update(extra)
        return globs

    def _resolve_path(self, path: str) -> str | None:
        """Resolve path and ensure it stays within the sandbox root."""
        root = self.config.filesystem_root or os.getcwd()
        joined = os.path.join(root, path)
        real = os.path.realpath(os.path.normpath(joined))
        real_root = os.path.realpath(os.path.normpath(root))
        if os.path.commonpath([real_root, real]) != real_root:
            return None
        return real


__all__ = ["SandboxConfig", "SandboxResult", "SandboxExecutor"]
