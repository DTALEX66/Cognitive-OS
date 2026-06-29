import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import app.learning.cards as cards_module
from app.learning.cards import create_card, due_cards, list_review_events, review_learning_card
from app.learning.fsrs import review_card, score_to_grade
from app.schemas import LearningCard


class LearningCardTests(unittest.TestCase):
    def setUp(self):
        temp_root = Path('data') / 'output'
        temp_root.mkdir(parents=True, exist_ok=True)
        self._temp_dir = tempfile.TemporaryDirectory(dir=temp_root)
        self._card_path = cards_module.CARD_PATH
        self._review_path = cards_module.REVIEW_PATH
        isolated = Path(self._temp_dir.name)
        cards_module.CARD_PATH = isolated / 'learning_cards.jsonl'
        cards_module.REVIEW_PATH = isolated / 'review_events.jsonl'

    def tearDown(self):
        cards_module.CARD_PATH = self._card_path
        cards_module.REVIEW_PATH = self._review_path
        self._temp_dir.cleanup()

    def test_score_to_grade(self):
        self.assertEqual(score_to_grade(0.0), 1)
        self.assertEqual(score_to_grade(0.5), 2)
        self.assertEqual(score_to_grade(0.8), 3)
        self.assertEqual(score_to_grade(0.95), 4)

    def test_review_card_updates_schedule(self):
        now = datetime(2026, 6, 29, tzinfo=timezone.utc)
        card = LearningCard(front='什么是路由？', back='路由是把输入分配到合适处理路径。', created_at=now.isoformat())

        updated, event = review_card(card, 0.95, now=now)

        self.assertEqual(event.grade, 4)
        self.assertEqual(updated.review_count, 1)
        self.assertGreater(updated.interval_seconds, 0)
        self.assertEqual(updated.last_review_at, now.isoformat())

    def test_store_review_and_due_cards(self):
        card = create_card('什么是记忆卡片？', '用于复习的最小知识单元。')
        now = datetime.now(timezone.utc) + timedelta(seconds=1)

        due_before = due_cards(now=now)
        updated, event = review_learning_card(card.id, 0.8, now=now)
        due_after = due_cards(now=now)
        events = list_review_events()

        self.assertEqual(len(due_before), 1)
        self.assertEqual(updated.review_count, 1)
        self.assertEqual(event.card_id, card.id)
        self.assertEqual(len(events), 1)
        self.assertEqual(due_after, [])

    def test_again_review_counts_lapse(self):
        now = datetime(2026, 6, 29, tzinfo=timezone.utc)
        card = create_card('难点', '需要重新学习。')
        updated, event = review_learning_card(card.id, 0.1, now=now + timedelta(days=2))

        self.assertEqual(event.grade, 1)
        self.assertEqual(updated.lapses, 1)


if __name__ == '__main__':
    unittest.main()
