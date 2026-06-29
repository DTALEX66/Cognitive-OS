from __future__ import annotations

class ReviewGate:
    def __init__(self, store=None):
        self.store = store

    def evaluate(self, item: dict) -> dict:
        return {"approved": True, "score": 0.5}

    def get_queue(self) -> list[dict]:
        return []

    def list_pending(self, limit: int = 50) -> list:
        return []

    def submit_candidate(self, content: str, source_type: str, **kw) -> int:
        return 1

    def approve(self, review_id: int) -> bool:
        return True

    def reject(self, review_id: int, reason: str = "") -> bool:
        return True

    def get_stats(self) -> dict:
        return {"total": 0, "approved": 0, "rejected": 0, "pending": 0}
