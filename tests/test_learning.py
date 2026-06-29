import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import app.learning.cards as cards_module
from app.learning.cards import create_card, due_cards, list_review_events, review_learning_card
from app.learning.fsrs import review_card, score_to_grade
from app.learning.rubrics import (
    RubricDimension,
    _closest_level,
    evaluate as rubric_evaluate,
    list_rubric_descriptions,
    weighted_total,
)
from app.learning.teach_back import (
    evaluate_session,
    get_session,
    list_methods,
    list_sessions,
    submit_explanation,
    weak_points,
)
from app.schemas import LearningCard
import app.learning.teach_back as teach_back


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


class RubricEngineTests(unittest.TestCase):
    def test_rubric_dimensions(self):
        dims = set(d.value for d in RubricDimension)
        self.assertEqual(dims, {'accuracy', 'completeness', 'depth', 'clarity'})

    def test_evaluate_short_text_detects_gaps(self):
        result = rubric_evaluate('路由是分配路径。', topic='routing')
        self.assertIn('explanation too brief to demonstrate understanding', result.gaps)
        self.assertIn('missing reasoning — no causal explanation provided', result.gaps)
        self.assertIn('lacks concrete examples or analogies', result.gaps)

    def test_evaluate_long_text_gets_higher_scores(self):
        text = (
            "路由是网络中将数据包从源地址转发到目标地址的过程。"
            "首先，路由器查看数据包的目标IP地址。"
            "然后，通过查找路由表决定最佳路径。"
            "例如，在家庭网络中，路由器将互联网流量分发到各个设备。"
            "这是因为不同子网需要中间设备来连接。"
            "就像邮局根据地址分拣信件一样。"
        )
        result = rubric_evaluate(text, topic='routing')
        self.assertGreater(result.weighted_total, 0.4)
        self.assertEqual(len(result.dimension_scores), 4)
        self.assertEqual(result.topic, 'routing')

    def test_evaluate_with_examples_and_causality(self):
        text = (
            "The OS scheduler allocates CPU time to processes because "
            "multiple processes cannot run simultaneously on a single core. "
            "For instance, the Linux CFS scheduler uses a red-black tree "
            "for fair time-sharing. This is like a round-robin tournament "
            "where each player gets a turn."
        )
        result = rubric_evaluate(text, topic='scheduler')
        self.assertGreater(result.dimension_scores.get('depth', 0), 0.3)
        self.assertGreater(result.dimension_scores.get('clarity', 0), 0.4)

    def test_weighted_total_function(self):
        scores = {'accuracy': 0.8, 'completeness': 0.7, 'depth': 0.5, 'clarity': 0.9}
        total = weighted_total(scores)
        expected = 0.8 * 0.35 + 0.7 * 0.30 + 0.5 * 0.20 + 0.9 * 0.15
        self.assertAlmostEqual(total, expected)

    def test_list_rubric_descriptions(self):
        descs = list_rubric_descriptions()
        self.assertEqual(len(descs), 4)
        for d in descs:
            self.assertIn('dimension', d)
            self.assertIn('weight', d)
            self.assertIn('levels', d)
            self.assertGreater(len(d['levels']), 0)


class ClosestLevelTests(unittest.TestCase):
    def test_closest_level_exact(self):
        levels = [(0.0, 'bad'), (0.5, 'ok'), (1.0, 'good')]
        score, desc = _closest_level(levels, 0.5)
        self.assertEqual(score, 0.5)
        self.assertEqual(desc, 'ok')

    def test_closest_level_rounds_up(self):
        levels = [(0.0, 'bad'), (0.35, 'ok'), (0.7, 'good')]
        score, desc = _closest_level(levels, 0.5)
        self.assertEqual(desc, 'ok')

    def test_closest_level_rounds_down(self):
        levels = [(0.0, 'bad'), (0.35, 'ok'), (0.7, 'good')]
        score, desc = _closest_level(levels, 0.6)
        self.assertEqual(desc, 'good')


class TeachBackEngineTests(unittest.TestCase):
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self._original_path = teach_back.TEACH_BACK_PATH
        isolated = Path(self._temp_dir.name)
        teach_back.TEACH_BACK_PATH = isolated / 'teach_back.jsonl'

    def tearDown(self):
        teach_back.TEACH_BACK_PATH = self._original_path
        self._temp_dir.cleanup()

    def test_list_methods(self):
        methods = list_methods()
        self.assertIn('feynman', methods)
        self.assertIn('analogy', methods)
        self.assertEqual(len(methods), 5)

    def test_submit_explanation_creates_session(self):
        session = submit_explanation('card_abc', '路由是将数据包从源发送到目标的过程。')
        self.assertEqual(session.card_id, 'card_abc')
        self.assertEqual(session.method, 'feynman')
        self.assertIsInstance(session.total_score, float)
        self.assertEqual(len(session.dimension_scores), 4)

    def test_submit_explanation_invalid_method_defaults(self):
        session = submit_explanation('card_abc', 'test', method='invalid_method')
        self.assertEqual(session.method, 'feynman')

    def test_list_sessions_by_card(self):
        submit_explanation('card_1', 'explanation 1')
        submit_explanation('card_2', 'explanation 2')
        submit_explanation('card_1', 'explanation 3')

        card1 = list_sessions(card_id='card_1')
        card2 = list_sessions(card_id='card_2')
        all_sessions = list_sessions()

        self.assertEqual(len(card1), 2)
        self.assertEqual(len(card2), 1)
        self.assertEqual(len(all_sessions), 3)

    def test_get_session_by_id(self):
        session = submit_explanation('card_abc', 'test get session')
        retrieved = get_session(session.id)
        self.assertIsNotNone(retrieved)
        if retrieved:
            self.assertEqual(retrieved.id, session.id)
            self.assertEqual(retrieved.explanation, 'test get session')

    def test_get_session_not_found(self):
        result = get_session('nonexistent_id')
        self.assertIsNone(result)

    def test_evaluate_session(self):
        session = submit_explanation('card_abc', 'a brief explanation')
        result = evaluate_session(session.id)
        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['session_id'], session.id)
            self.assertIn('total_score', result)
            self.assertIn('dimension_scores', result)
            self.assertIn('gaps', result)
            self.assertIn('dimension_feedback', result)

    def test_evaluate_session_not_found(self):
        result = evaluate_session('nonexistent')
        self.assertIsNone(result)

    def test_weak_points_empty_card(self):
        wp = weak_points('nonexistent_card')
        self.assertEqual(wp['total_sessions'], 0)
        self.assertEqual(wp['average_score'], 0.0)
        self.assertEqual(wp['recurring_gaps'], [])

    def test_weak_points_aggregates_gaps(self):
        submit_explanation('card_gap', 'too short')
        submit_explanation('card_gap', 'also too short with no example because?')
        submit_explanation('card_gap', 'again short, no reasoning because?')

        wp = weak_points('card_gap')
        self.assertEqual(wp['total_sessions'], 3)
        self.assertGreater(len(wp['all_gaps']), 0)
        self.assertIn('card_id', wp)
        self.assertGreater(wp['average_score'], 0)

    def test_weak_points_dimension_averages(self):
        submit_explanation(
            'card_dim',
            '首先，这是第一步。其次，这是第二步。最后，第三步。'
            '这是因为有因果关系。例如，这个例子说明问题。'
        )
        wp = weak_points('card_dim')
        self.assertIn('dimension_averages', wp)
        self.assertEqual(len(wp['dimension_averages']), 4)


if __name__ == '__main__':
    unittest.main()
