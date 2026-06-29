"""Setup Engine - workspace detection + git root"""

from __future__ import annotations
import os
import subprocess


class SetupEngine:
    def __init__(self, store=None):
        self._store = store

    def detect_workspace(self, path="."):
        git = self._find_git_root(path)
        py = self._find_python_root(path)
        return {"git_root": git, "python_root": py, "cwd": os.path.abspath(path)}

    def _find_git_root(self, path):
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                cwd=path,
                timeout=5,
            )
            return r.stdout.strip() if r.returncode == 0 else None
        except:
            return None

    def _find_python_root(self, path):
        p = os.path.abspath(path)
        while p:
            if os.path.exists(os.path.join(p, "setup.py")) or os.path.exists(
                os.path.join(p, "pyproject.toml")
            ):
                return p
            parent = os.path.dirname(p)
            if parent == p:
                break
            p = parent
        return None
