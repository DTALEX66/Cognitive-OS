import tempfile
import unittest
from pathlib import Path

import app.tools.registry as registry
from app.tools.registry import run_tool


class ToolGuardTests(unittest.TestCase):
    def setUp(self):
        temp_root = Path('data') / 'output'
        temp_root.mkdir(parents=True, exist_ok=True)
        self._temp_dir = tempfile.TemporaryDirectory(dir=temp_root)
        self._safe_output_dir = registry.SAFE_OUTPUT_DIR
        registry.SAFE_OUTPUT_DIR = Path(self._temp_dir.name)

    def tearDown(self):
        registry.SAFE_OUTPUT_DIR = self._safe_output_dir
        self._temp_dir.cleanup()

    def test_safe_write_defaults_to_dry_run(self):
        result = run_tool('safe_write', {'filename': 'note.txt', 'content': 'hello'})

        self.assertEqual(result['status'], 'ok')
        self.assertTrue(result['dry_run'])
        self.assertIn('medium_risk_dry_run', result['guard']['reasons'])
        self.assertFalse((registry.SAFE_OUTPUT_DIR / 'note.txt').exists())

    def test_safe_write_can_write_with_explicit_dry_run_false(self):
        result = run_tool(
            'safe_write',
            {'filename': 'note.txt', 'content': 'hello'},
            dry_run=False,
        )

        self.assertEqual(result['status'], 'ok')
        self.assertFalse(result['dry_run'])
        self.assertTrue(result['written'])
        self.assertIn('medium_risk_explicit_execution_requested', result['guard']['reasons'])
        self.assertEqual((registry.SAFE_OUTPUT_DIR / 'note.txt').read_text(encoding='utf-8'), 'hello')

    def test_safe_write_blocks_path_traversal(self):
        result = run_tool('safe_write', {'filename': '../outside.txt', 'content': 'bad'}, dry_run=False)

        self.assertEqual(result['status'], 'blocked')
        self.assertFalse(result['guard']['allowed'])
        self.assertIn('safe_write_target_must_stay_under_data_output', result['guard']['reasons'])

    def test_file_read_blocks_path_outside_project(self):
        result = run_tool('file_read', {'path': '..\\AGENTS.md'})

        self.assertEqual(result['status'], 'blocked')
        self.assertFalse(result['guard']['allowed'])
        self.assertIn('path_must_stay_inside_project_root', result['guard']['reasons'])

    def test_code_exec_is_blocked_by_guard(self):
        result = run_tool('code_exec', {'code': 'print(1)'}, dry_run=False)

        self.assertEqual(result['status'], 'blocked')
        self.assertTrue(result['dry_run'])
        self.assertFalse(result['guard']['allowed'])
        self.assertIn('high_risk_tool_blocked', result['guard']['reasons'])
        self.assertEqual(result['code_preview'], 'print(1)')


if __name__ == '__main__':
    unittest.main()
