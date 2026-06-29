from __future__ import annotations
from typing import Optional

class LearningSystem:
    def __init__(self, store=None):
        self.store = store

    def get_profile(self):
        return {}

    def create_card(self, title: str, content: str, *args, **kwargs) -> int:
        return 1

    def review_card(self, card_id: int, score: float) -> dict:
        return {"strength": score, "next_review": ""}

    def schedule_review(self, card_id: int):
        pass

    def due_cards(self, limit: int = 50) -> list:
        return []

    def list_cards(self, deck: str = "", limit: int = 50) -> list:
        return []

    def list_routes(self, limit: int = 20) -> list:
        return []

    def get_route(self, route_id: int):
        return None

    def list_palace(self) -> list:
        return []

    def add_palace_node(self, title: str, node_type: str = "concept", **kw):
        return 0

    def get_cognitive_load(self):
        return {}

    def get_encoding(self):
        return {}

    def record_review(self, card_id: int, score: int, elapsed: float):
        pass

    def get_stats(self):
        return {"cards_total": 0, "cards_due": 0, "reviews_today": 0}
