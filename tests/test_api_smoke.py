import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import app.core.trace as trace_module
import app.learning.cards as cards_module
import app.memory.store as store_module
from app.main import app


class ApiSmokeTests(unittest.TestCase):
    def setUp(self):
        temp_root = Path('data') / 'output'
        temp_root.mkdir(parents=True, exist_ok=True)
        self._temp_dir = tempfile.TemporaryDirectory(dir=temp_root)
        self._memory_path = store_module.MEMORY_PATH
        self._lesson_path = store_module.LESSON_PATH
        self._trace_path = trace_module.TRACE_PATH
        self._card_path = cards_module.CARD_PATH
        self._review_path = cards_module.REVIEW_PATH

        isolated = Path(self._temp_dir.name)
        store_module.MEMORY_PATH = isolated / 'memory.jsonl'
        store_module.LESSON_PATH = isolated / 'lessons.jsonl'
        trace_module.TRACE_PATH = isolated / 'trace.jsonl'
        cards_module.CARD_PATH = isolated / 'learning_cards.jsonl'
        cards_module.REVIEW_PATH = isolated / 'review_events.jsonl'
        self.client = TestClient(app)

    def tearDown(self):
        store_module.MEMORY_PATH = self._memory_path
        store_module.LESSON_PATH = self._lesson_path
        trace_module.TRACE_PATH = self._trace_path
        cards_module.CARD_PATH = self._card_path
        cards_module.REVIEW_PATH = self._review_path
        self._temp_dir.cleanup()

    def test_health_and_tools(self):
        health = self.client.get('/health')
        tools = self.client.get('/tools')

        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()['status'], 'ok')
        self.assertEqual(tools.status_code, 200)
        self.assertGreaterEqual(len(tools.json()['items']), 1)

    def test_route_review_for_high_risk_input(self):
        response = self.client.post('/route', json={'content': '删除系统配置'})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['route'], 'REVIEW')
        self.assertEqual(payload['risk_level'], 'high')

    def test_run_writes_memory_trace_and_lesson(self):
        run_response = self.client.post(
            '/run',
            json={'content': '继续修复路由并整理项目结构', 'source': 'api-smoke'},
        )
        search_response = self.client.post('/memory/search', json={'query': '路由修复'})
        traces_response = self.client.get('/traces')
        lessons_response = self.client.get('/memory/lessons')

        self.assertEqual(run_response.status_code, 200)
        run_payload = run_response.json()
        self.assertEqual(run_payload['status'], 'done')
        self.assertEqual(run_payload['route']['route'], 'TASK')
        self.assertGreater(run_payload['context']['score'], 0)
        self.assertIn('audit', run_payload['eval'])
        self.assertEqual(run_payload['eval']['audit']['event_count'], 3)
        self.assertIn('successful pipeline', run_payload['lesson']['pattern'])
        self.assertEqual(search_response.status_code, 200)
        self.assertGreaterEqual(len(search_response.json()['items']), 1)
        self.assertGreaterEqual(len(traces_response.json()['items']), 1)
        self.assertGreaterEqual(len(lessons_response.json()['items']), 1)

    def test_learning_card_review_flow(self):
        create_response = self.client.post(
            '/learning/cards',
            json={'front': '什么是路由？', 'back': '路由把输入分配到 KB、IR、TASK 等处理路径。'},
        )
        card = create_response.json()['card']
        review_response = self.client.post('/learning/review', json={'card_id': card['id'], 'score': 0.9})
        due_response = self.client.get('/learning/due')

        self.assertEqual(create_response.status_code, 200)
        self.assertEqual(review_response.status_code, 200)
        self.assertEqual(review_response.json()['event']['grade'], 4)
        self.assertEqual(due_response.status_code, 200)
        self.assertEqual(due_response.json()['items'], [])


if __name__ == '__main__':
    unittest.main()
