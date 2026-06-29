"""Prompt Engine - system prompts management"""

from __future__ import annotations


class PromptEngine:
    def __init__(self, store=None):
        self._store = store
        self._prompts = {}

    def register(self, name, prompt):
        self._prompts[name] = prompt

    def get(self, name):
        return self._prompts.get(name, "")

    def list(self):
        return list(self._prompts.keys())
