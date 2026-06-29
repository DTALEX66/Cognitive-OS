import unittest

from app.evaluation.evaluator import evaluate
from app.evaluation.feedback import compile_lesson
from app.evaluation.trace_audit import audit_trace
from app.schemas import ExecutionTrace


def trace_with_result(status: str = 'ok', success: bool = True) -> ExecutionTrace:
    return ExecutionTrace(
        task_id='task_test',
        events=[
            {
                'step': {'id': 1, 'name': 'test_step', 'tool': 'echo'},
                'result': {'tool': 'echo', 'status': status, 'dry_run': False},
            }
        ],
        result={'status': 'done' if success else 'completed_with_errors'},
        success=success,
    )


class TraceAuditTests(unittest.TestCase):
    def test_success_trace_passes_audit(self):
        trace = trace_with_result()
        audit = audit_trace(trace)
        eval_result = evaluate(trace)
        lesson = compile_lesson(eval_result, trace)

        self.assertTrue(audit.success)
        self.assertEqual(audit.score, 1.0)
        self.assertTrue(eval_result.success)
        self.assertEqual(eval_result.audit['event_count'], 1)
        self.assertEqual(lesson.lesson_type, 'success')
        self.assertIn('successful pipeline', lesson.pattern)

    def test_blocked_trace_creates_constraint_lesson(self):
        trace = trace_with_result(status='blocked', success=False)
        eval_result = evaluate(trace)
        lesson = compile_lesson(eval_result, trace)

        self.assertFalse(eval_result.success)
        self.assertIn('blocked_tool_result', eval_result.issues)
        self.assertEqual(eval_result.failure_reason, 'blocked tool result')
        self.assertEqual(lesson.lesson_type, 'constraint')
        self.assertIn('blocked tool execution', lesson.pattern)

    def test_missing_result_trace_creates_antipattern_lesson(self):
        trace = ExecutionTrace(
            task_id='task_missing',
            events=[{'step': {'id': 1, 'name': 'missing_result', 'tool': 'echo'}}],
            result={'status': 'completed_with_errors'},
            success=False,
        )
        eval_result = evaluate(trace)
        lesson = compile_lesson(eval_result, trace)

        self.assertIn('missing_tool_result', eval_result.issues)
        self.assertEqual(lesson.lesson_type, 'anti_pattern')
        self.assertIn('lacked sufficient evidence', lesson.pattern)


if __name__ == '__main__':
    unittest.main()
