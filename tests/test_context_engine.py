import unittest

from app.rag.context_engine import build_context_pack, estimate_tokens
from app.schemas import CoreObject


class ContextEngineTests(unittest.TestCase):
    def test_build_context_pack_scores_chinese_overlap(self):
        items = [
            CoreObject(
                content='继续修复路由并整理项目结构',
                source='api-smoke',
                metadata={'quality_score': 0.9},
            )
        ]

        pack = build_context_pack('路由修复', items, top_k=5)

        self.assertEqual(pack.query, '路由修复')
        self.assertGreater(pack.score, 0.5)
        self.assertIn('quality_signal=', pack.score_reasons[3])
        self.assertIn('api-smoke', pack.summary)

    def test_estimate_tokens_is_stable_for_short_text(self):
        self.assertEqual(estimate_tokens('abcd'), 1)
        self.assertEqual(estimate_tokens(''), 0)


if __name__ == '__main__':
    unittest.main()
