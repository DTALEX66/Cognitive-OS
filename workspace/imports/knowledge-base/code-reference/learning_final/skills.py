"""Skills Engine - Skill practice with sandbox ()"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
import json

class SandboxContext:
    """Sandbox security context"""
    def __init__(self, allowed_commands=None, max_timeout=30, workspace_only=True):
        self.allowed_commands = allowed_commands or ["python", "node", "npm test", "pytest", "cargo"]
        self.max_timeout = max_timeout
        self.workspace_only = workspace_only
    def validate_command(self, command: str) -> dict:
        if any(cmd in command for cmd in ["rm -rf", "sudo", "mkfs", "dd if=", "> /dev/"]):
            return {"allowed": False, "reason": "destructive command blocked"}
        if self.workspace_only and ".." in command.split():
            return {"allowed": False, "reason": "path escape blocked"}
        if len(command) > 1000:
            return {"allowed": False, "reason": "command too long"}
        allowed = any(command.startswith(cmd) for cmd in self.allowed_commands)
        return {"allowed": allowed, "reason": "command not in allowed list" if not allowed else "ok"}
    
    def validate_path(self, path: str) -> dict:
        bad_patterns = ["~", "$HOME", "..", "/etc/", "/usr/", "/bin/", "/boot/", "/dev/"]
        for p in bad_patterns:
            if p in path:
                return {"allowed": False, "reason": f"path contains forbidden: {p}"}
        return {"allowed": True, "reason": "ok"}

class Skill:
    def __init__(self, name: str, domain: str, difficulty: int, description: str, prompt: str = ""):
        self.name = name
        self.domain = domain
        self.difficulty = difficulty
        self.description = description
        self.prompt = prompt

class SkillEngine:
    """ - skill management with sandboxed execution"""
    def __init__(self, store=None):
        self._store = store
        self._sandbox = SandboxContext()
        self._skills = {}
    def register(self, name: str, skill: Skill):
        self._skills[name] = skill
    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)
    def list(self, domain: str = "", status: str = ""):
        if self._store:
            query = "SELECT id, title, task_type, target_skill, difficulty, created_at FROM skill_tasks"
            params = []
            conditions = []
            if domain:
                conditions.append("target_skill LIKE ?")
                params.append(f"%{domain}%")
            if status == "completed":
                conditions.append("id IN (SELECT task_id FROM skill_attempts)")
            elif status == "pending":
                conditions.append("id NOT IN (SELECT task_id FROM skill_attempts)")
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC LIMIT 100"
            try:
                rows = self._store.conn.execute(query, params).fetchall()
                return [{"id": r[0], "title": r[1], "type": r[2], "target": r[3], "difficulty": r[4], "created": r[5]} for r in rows]
            except: pass
        return list(self._skills.values())
    def create_task(self, name: str, domain: str, difficulty: int, description: str = "") -> int:
        if self._store:
            ts = datetime.now(timezone.utc).isoformat()
            cur = self._store.conn.execute(
                "INSERT INTO skill_tasks (title, task_type, target_skill, expected_output, rubric_json, difficulty, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
                (name, "practice", domain, description, "{}", difficulty, ts, ts))
            self._store.conn.commit()
            skill = Skill(name, domain, difficulty, description)
            self._skills[name] = skill
            return cur.lastrowid
        return 0
    def complete_task(self, task_id: int, evidence: str = "", score: float = 1.0, time_spent: int = 0) -> dict:
        if self._store:
            ts = datetime.now(timezone.utc).isoformat()
            self._store.conn.execute(
                "INSERT INTO skill_attempts (task_id, output_text, rubric_score, feedback_json, created_at) VALUES (?,?,?,?,?)",
                (task_id, evidence, score, json.dumps({"time_spent": time_spent}), ts))
            self._store.conn.commit()
            return {"task_id": task_id, "score": score, "time_spent": time_spent}
        return {"task_id": task_id, "score": score}
    def sandbox_execute(self, command: str, timeout: int = 30) -> dict:
        validation = self._sandbox.validate_command(command)
        if not validation["allowed"]:
            return {"success": False, "error": validation["reason"]}
        return {"success": True, "command": command, "sandbox_mode": True, "timeout": min(timeout, self._sandbox.max_timeout)}

    def attempt_task(self, task_id: int, output_text: str, score: float) -> int:
        if self._store:
            try:
                ts = datetime.now(timezone.utc).isoformat()
                cur = self._store.conn.execute(
                    "INSERT INTO skill_attempts (task_id, output_text, rubric_score, feedback_json, created_at) VALUES (?,?,?,?,?)",
                    (task_id, output_text, score, json.dumps({"auto_graded": True}), ts))
                self._store.conn.commit()
                return cur.lastrowid
            except:
                pass
        return 0

    def list_tasks(self, task_type: str = "", limit: int = 20) -> list:
        """List skill tasks, compatible with API router call."""
        if self._store:
            query = "SELECT id, title, task_type, target_skill, difficulty, created_at FROM skill_tasks"
            params = []
            conditions = []
            if task_type:
                conditions.append("task_type = ?")
                params.append(task_type)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_at DESC"
            if limit > 0:
                query += " LIMIT ?"
                params.append(limit)
            try:
                rows = self._store.conn.execute(query, params).fetchall()
                return [{"id": r[0], "title": r[1], "type": r[2], "target": r[3], "difficulty": r[4], "created": r[5]} for r in rows]
            except Exception:
                pass
        return []

    def average_score(self, domain: str) -> float:
        if self._store:
            try:
                row = self._store.conn.execute(
                    "SELECT AVG(sa.rubric_score) FROM skill_attempts sa JOIN skill_tasks st ON sa.task_id = st.id WHERE st.target_skill LIKE ?",
                    (f"%{domain}%",)).fetchone()
                return row[0] if row and row[0] else 0.5
            except:
                pass
        return 0.5
