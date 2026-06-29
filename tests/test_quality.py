import unittest

from app.api.ingest import ingest
from app.core.router import route
from app.ingestion.quality import assess_content_quality


class ContentQualityTests(unittest.TestCase):
    def test_blocked_web_content_is_detected(self):
        quality = assess_content_quality('Access denied. Please verify you are human.', source_type='web')

        self.assertTrue(quality.looks_blocked)
        self.assertIn('looks_blocked', quality.issues)
        self.assertLess(quality.score, 0.6)

    def test_ingest_adds_quality_metadata(self):
        doc = ingest({'content': '这是一段用于学习和整理的知识笔记。', 'source': 'manual'})

        self.assertIn('quality_score', doc.metadata)
        self.assertIn('quality_issues', doc.metadata)

    def test_blocked_content_routes_to_review(self):
        doc = ingest({'content': 'Access denied. Please verify you are human.', 'type': 'web'})
        decision = route(doc)

        self.assertEqual(decision.route, 'REVIEW')
        self.assertEqual(decision.risk_level, 'medium')


if __name__ == '__main__':
    unittest.main()
