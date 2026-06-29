"""Doctor module ? environment health checks."""
from __future__ import annotations
import sys
import sqlite3
from typing import Any
from types import SimpleNamespace

class Doctor:
    REQUIRED_PACKAGES = ["fastapi", "uvicorn", "typer", "httpx"]
    OPTIONAL_PACKAGES = ["markitdown", "docling", "selenium", "crawl4ai", "litellm"]

    def __init__(self, store: Any | None = None) -> None:
        self._store = store

    def run_all(self) -> list[dict]:
        results = []
        results.append(self._check_python())
        results.extend(self._check_packages())
        results.append(self._check_sqlite())
        if self._store:
            results.append(self._check_db())
        return results

    def _check_python(self) -> dict:
        v = sys.version_info
        ok = v.major >= 3 and v.minor >= 10
        return {"name": "python", "status": "OK" if ok else "WARN", "detail": f"{v.major}.{v.minor}.{v.micro}"}

    def _check_packages(self) -> list[dict]:
        results = []
        for pkg in self.REQUIRED_PACKAGES:
            try:
                __import__(pkg)
                results.append({"name": pkg, "status": "OK", "detail": ""})
            except ImportError:
                results.append({"name": pkg, "status": "FAIL", "detail": "not installed"})
        for pkg in self.OPTIONAL_PACKAGES:
            try:
                __import__(pkg)
                results.append({"name": pkg, "status": "OK", "detail": "optional"})
            except ImportError:
                pass
        return results

    def _check_sqlite(self) -> dict:
        try:
            v = sqlite3.sqlite_version
            return {"name": "sqlite", "status": "OK", "detail": v}
        except Exception as e:
            return {"name": "sqlite", "status": "FAIL", "detail": str(e)}

    def _check_db(self) -> dict:
        try:
            self._store._cursor.execute("SELECT 1")
            return {"name": "database", "status": "OK", "detail": ""}
        except Exception as e:
            return {"name": "database", "status": "FAIL", "detail": str(e)}

def run_doctor() -> list:
    '''Run all checks and return objects with .name/.ok/.status/.detail.'''
    d = Doctor()
    results = []
    for item in d.run_all():
        item["ok"] = item.get("status", "") == "OK"
        results.append(SimpleNamespace(**item))
    return results
