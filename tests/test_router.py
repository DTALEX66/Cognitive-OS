import unittest

from app.api.ingest import ingest
from app.core.router import route


class RouterKeywordTests(unittest.TestCase):
    def decision_for(self, content: str):
        return route(ingest({'content': content}))

    def test_low_value_chinese_input_is_dropped(self):
        decision = self.decision_for('好的')

        self.assertEqual(decision.route, 'DROP')

    def test_chinese_knowledge_input_routes_to_kb(self):
        decision = self.decision_for('学习 笔记 总结')

        self.assertEqual(decision.route, 'KB')

    def test_chinese_research_input_routes_to_ir(self):
        decision = self.decision_for('调研 GitHub 开源项目框架')

        self.assertEqual(decision.route, 'IR')

    def test_chinese_task_input_routes_to_task(self):
        decision = self.decision_for('继续 修复 项目 路由')

        self.assertEqual(decision.route, 'TASK')
        self.assertEqual(decision.risk_level, 'low')

    def test_high_risk_chinese_input_requires_review(self):
        decision = self.decision_for('删除系统配置')

        self.assertEqual(decision.route, 'REVIEW')
        self.assertEqual(decision.risk_level, 'high')


if __name__ == '__main__':
    unittest.main()
