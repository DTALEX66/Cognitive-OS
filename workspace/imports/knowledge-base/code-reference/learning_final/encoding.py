"""Encoding Engine - Memory encoding with Zod v4 validation chain ()"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Optional
import json
import re

class ValidationChain:
    """Zod v4 discriminated union chain pattern"""
    def __init__(self):
        self._rules = []
    def add(self, rule_name, validator):
        self._rules.append((rule_name, validator))
        return self
    def validate(self, data: dict) -> dict:
        errors = []
        for name, validator in self._rules:
            result = validator(data)
            if result is not True:
                errors.append({"rule": name, "error": result})
        return {"valid": len(errors) == 0, "errors": errors}

class EncodingEngine:
    def __init__(self, store=None):
        self._store = store
        self._validator = ValidationChain()
        self._validator             .add("required_fields", lambda d: True if d.get("title") and d.get("content") else "title and content required")             .add("title_length", lambda d: True if len(d.get("title", "")) <= 200 else "title too long (max 200)")             .add("content_length", lambda d: True if len(d.get("content", "")) <= 10000 else "content too long (max 10000)")             .add("tags_type", lambda d: True if isinstance(d.get("tags", ""), str) else "tags must be string")
    def validate(self, data: dict) -> dict:
        return self._validator.validate(data)
    def encode(self, text: str, tags: str = "") -> dict:
        return {"text": text, "length": len(text), "tags": tags}
    def decode(self, data: dict) -> str:
        return data.get("text", "")
    def encode_qa(self, question: str, answer: str, tags: str = "") -> dict:
        return {"question": question, "answer": answer, "type": "qa", "tags": tags}
    def suggest_encoding_strategy(self, material_type: str) -> str:
        strategies = {
            "concept": "visual+mnemonic",
            "procedure": "step_by_step+flowchart",
            "fact": "qa+spaced_repetition",
            "code": "annotation+practice",
            "formula": "derivation+visual",
        }
        return strategies.get(material_type, "qa+spaced_repetition")

    def suggest(self, content_text: str, source_type: str, source_id: int) -> dict:
        strategies = self.suggest_encoding_strategy(source_type)
        return {"suggestions": [{"strategy": strategies, "confidence": 0.7}], "content_length": len(content_text)}

    def save(self, encoding_type: str, content: str, source_type: str, source_id: int, score: float) -> int:
        if self._store:
            try:
                ts = datetime.now(timezone.utc).isoformat()
                cur = self._store.conn.execute(
                    "INSERT INTO memory_encodings (source_type, source_id, encoding_type, content, fit_score, created_at) VALUES (?,?,?,?,?,?)",
                    (source_type, source_id, encoding_type, content, score, ts))
                self._store.conn.commit()
                return cur.lastrowid
            except:
                pass
        return 0

    def list_by_source(self, source_type: str, source_id: int) -> list:
        if self._store:
            try:
                rows = self._store.conn.execute(
                    "SELECT id, encoding_type, content, fit_score, created_at FROM memory_encodings WHERE source_type=? AND source_id=? ORDER BY created_at DESC",
                    (source_type, source_id)).fetchall()
                return [{"id": r[0], "type": r[1], "content": r[2][:100], "score": r[3], "created": r[4]} for r in rows]
            except:
                pass
        return []



def encoding_fit_score(concept_type_fit=0.5, visualizability=0.5):
    return round((concept_type_fit * 0.55 + visualizability * 0.45), 3)
