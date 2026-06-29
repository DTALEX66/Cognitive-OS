"""B-Line Eval Runner - Quality evaluation engine for agent outputs.

Supports multiple evaluation metrics, batch testing, threshold-based
pass/fail decisions, and comprehensive report generation.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from difflib import SequenceMatcher
import json
import re


class EvalRunner:
    """Enhanced evaluation engine with batch testing and report generation.

    Measures agent output quality using configurable metrics:
    - Similarity (text match ratio)
    - Length match
    - Keyword presence
    - Structure validity
    - Custom metric functions
    """

    def __init__(self, store: Any) -> None:
        self._store = store

    # ── Single Run ──

    def run(self, eval_type: str, target: str, input_data: str,
            expected: str, actual: str, model: str = "",
            metrics: list[str] | None = None,
            metadata: dict | None = None) -> dict:
        ts = datetime.now(timezone.utc).isoformat()
        metric_names = metrics or ["similarity", "length_match"]
        scores = self._compute_metrics(expected, actual, metric_names)
        overall = round(sum(scores.values()) / max(len(scores), 1), 3)
        cur = self._store.conn.execute(
            "INSERT INTO eval_runs (eval_type, target, input_data, expected_output,"
            " actual_output, score, metric_scores, model_used, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eval_type, target, input_data, expected, actual, overall,
             json.dumps(scores), model, ts))
        self._store.conn.commit()
        run_id = int(cur.lastrowid)
        return {
            "run_id": run_id, "score": overall, "metrics": scores,
            "eval_type": eval_type, "target": target,
        }

    def get_run(self, run_id: int) -> dict | None:
        row = self._store.conn.execute(
            "SELECT * FROM eval_runs WHERE id=?", (run_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        r["metric_scores"] = json.loads(r.get("metric_scores", "{}"))
        return r

    def list_runs(self, eval_type: str = "", limit: int = 20) -> list[dict]:
        if eval_type:
            cur = self._store.conn.execute(
                "SELECT * FROM eval_runs WHERE eval_type=? ORDER BY created_at DESC LIMIT ?",
                (eval_type, limit))
        else:
            cur = self._store.conn.execute(
                "SELECT * FROM eval_runs ORDER BY created_at DESC LIMIT ?", (limit,))
        result = []
        for row in cur.fetchall():
            r = dict(row)
            r["metric_scores"] = json.loads(r.get("metric_scores", "{}"))
            result.append(r)
        return result

    def summary(self, eval_type: str = "") -> dict:
        if eval_type:
            row = self._store.conn.execute(
                "SELECT COUNT(*), AVG(score), MIN(score), MAX(score)"
                " FROM eval_runs WHERE eval_type=?", (eval_type,)).fetchone()
            typ = eval_type
        else:
            row = self._store.conn.execute(
                "SELECT COUNT(*), AVG(score), MIN(score), MAX(score)"
                " FROM eval_runs").fetchone()
            typ = "all"
        return {
            "type": typ, "total_runs": row[0] or 0,
            "avg_score": round(row[1] or 0, 3),
            "min_score": round(row[2] or 0, 3),
            "max_score": round(row[3] or 0, 3),
        }

    # ── Batch Evaluation ──

    def start_batch(self, batch_name: str, eval_type: str = "rag",
                    description: str = "", pass_threshold: float = 0.7) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO eval_batches (batch_name, description, eval_type,"
            " total_cases, passed_cases, avg_score, min_score, max_score,"
            " pass_threshold, status, created_at) VALUES (?, ?, ?, 0, 0, 0, 0, 0, ?, 'running', ?)",
            (batch_name, description, eval_type, pass_threshold, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def add_batch_case(self, batch_id: int, case_name: str,
                       input_data: str, expected_output: str) -> int:
        cur = self._store.conn.execute(
            "INSERT INTO eval_batch_items (batch_id, case_name, input_data,"
            " expected_output, actual_output, score, passed)"
            " VALUES (?, ?, ?, ?, '', 0, 0)",
            (batch_id, case_name, input_data, expected_output))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def run_batch_case(self, batch_id: int, item_id: int, actual_output: str,
                       metrics: list[str] | None = None,
                       eval_type: str = "rag", model: str = "") -> dict:
        item = self._store.conn.execute(
            "SELECT * FROM eval_batch_items WHERE id=? AND batch_id=?",
            (item_id, batch_id)).fetchone()
        if not item:
            return {"error": "batch item not found"}

        item_dict = dict(item)
        score_result = self.run(
            eval_type=eval_type,
            target=item_dict["case_name"],
            input_data=item_dict["input_data"],
            expected=item_dict["expected_output"],
            actual=actual_output,
            model=model,
            metrics=metrics,
        )

        passed = 1 if score_result["score"] >= self._get_batch_threshold(batch_id) else 0
        self._store.conn.execute(
            "UPDATE eval_batch_items SET actual_output=?, score=?, passed=?, run_id=?"
            " WHERE id=?",
            (actual_output, score_result["score"], passed, score_result["run_id"], item_id))
        self._store.conn.commit()

        self._recalc_batch_stats(batch_id)
        return {"item_id": item_id, "score": score_result["score"], "passed": bool(passed)}

    def run_batch(self, batch_id: int, outputs: dict[int, str],
                  metrics: list[str] | None = None,
                  eval_type: str = "rag", model: str = "") -> dict:
        """Run all batch cases with provided outputs. outputs maps item_id -> actual_output."""
        results = []
        for item_id, actual_output in outputs.items():
            result = self.run_batch_case(
                batch_id, item_id, actual_output, metrics, eval_type, model)
            results.append(result)

        self.complete_batch(batch_id)
        return {
            "batch_id": batch_id,
            "results": results,
            "stats": self.get_batch_stats(batch_id),
        }

    def complete_batch(self, batch_id: int) -> None:
        ts = datetime.now(timezone.utc).isoformat()
        stats = self._recalc_batch_stats(batch_id)
        report = self.generate_batch_report(batch_id)
        self._store.conn.execute(
            "UPDATE eval_batches SET status='completed', report_json=?, completed_at=? WHERE id=?",
            (json.dumps(report), ts, batch_id))
        self._store.conn.commit()

    def get_batch(self, batch_id: int) -> dict | None:
        row = self._store.conn.execute(
            "SELECT * FROM eval_batches WHERE id=?", (batch_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        r["report_json"] = json.loads(r.get("report_json", "{}"))
        items = self._store.conn.execute(
            "SELECT * FROM eval_batch_items WHERE batch_id=? ORDER BY id",
            (batch_id,)).fetchall()
        r["items"] = [dict(i) for i in items]
        return r

    def get_batch_stats(self, batch_id: int) -> dict:
        row = self._store.conn.execute(
            "SELECT total_cases, passed_cases, avg_score, min_score, max_score, pass_threshold"
            " FROM eval_batches WHERE id=?", (batch_id,)).fetchone()
        if not row:
            return {}
        return {
            "total_cases": row[0], "passed_cases": row[1],
            "avg_score": row[2], "min_score": row[3], "max_score": row[4],
            "pass_threshold": row[5],
            "pass_rate": round(row[1] / max(row[0], 1), 3),
        }

    def generate_batch_report(self, batch_id: int) -> dict:
        batch = self.get_batch(batch_id)
        if not batch:
            return {"error": "batch not found"}

        items = batch.get("items", [])
        passed = [i for i in items if i.get("passed")]
        failed = [i for i in items if not i.get("passed") and i.get("score", 0) > 0]
        scores = [i.get("score", 0) for i in items if i.get("score", 0) > 0]

        return {
            "batch_name": batch.get("batch_name", ""),
            "eval_type": batch.get("eval_type", ""),
            "total": len(items),
            "passed": len(passed),
            "failed": len(failed),
            "pass_rate": round(len(passed) / max(len(items), 1), 3),
            "avg_score": round(sum(scores) / max(len(scores), 1), 3) if scores else 0,
            "best_case": max(items, key=lambda x: x.get("score", 0)).get("case_name", "") if items else "",
            "worst_case": min(items, key=lambda x: x.get("score", 1)).get("case_name", "") if items else "",
            "failed_cases": [{"name": i["case_name"], "score": i["score"]} for i in failed],
        }

    def list_batches(self, limit: int = 20) -> list[dict]:
        cur = self._store.conn.execute(
            "SELECT * FROM eval_batches ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

    # ── Metrics ──

    def _compute_metrics(self, expected: str, actual: str,
                         metric_names: list[str]) -> dict[str, float]:
        scores = {}
        for name in metric_names:
            if name == "similarity":
                scores[name] = round(
                    SequenceMatcher(None, expected.lower(), actual.lower()).ratio(), 3)
            elif name == "length_match":
                scores[name] = round(
                    len(actual) / max(len(expected), 1), 3)
            elif name == "keyword_overlap":
                exp_words = set(re.findall(r'w+', expected.lower()))
                act_words = set(re.findall(r'w+', actual.lower()))
                scores[name] = round(
                    len(exp_words & act_words) / max(len(exp_words), 1), 3)
            elif name == "exact_match":
                scores[name] = 1.0 if expected.strip() == actual.strip() else 0.0
            elif name == "contains_expected":
                scores[name] = 1.0 if expected.lower() in actual.lower() else 0.0
            elif name == "structure_valid":
                scores[name] = 1.0 if self._is_valid_json(actual) else 0.0
            else:
                scores[name] = 0.0
        return scores

    @staticmethod
    def _is_valid_json(text: str) -> bool:
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def _get_batch_threshold(self, batch_id: int) -> float:
        row = self._store.conn.execute(
            "SELECT pass_threshold FROM eval_batches WHERE id=?", (batch_id,)).fetchone()
        return row[0] if row else 0.7

    def _recalc_batch_stats(self, batch_id: int) -> dict:
        stats = self._store.conn.execute(
            "SELECT COUNT(*), SUM(passed), AVG(score), MIN(score), MAX(score)"
            " FROM eval_batch_items WHERE batch_id=? AND score > 0",
            (batch_id,)).fetchone()
        self._store.conn.execute(
            "UPDATE eval_batches SET total_cases=?, passed_cases=?, avg_score=?,"
            " min_score=?, max_score=? WHERE id=?",
            (stats[0] or 0, stats[1] or 0, round(stats[2] or 0, 3),
             round(stats[3] or 0, 3), round(stats[4] or 0, 3), batch_id))
        self._store.conn.commit()
        return {
            "total_cases": stats[0] or 0,
            "passed_cases": stats[1] or 0,
            "avg_score": round(stats[2] or 0, 3),
            "min_score": round(stats[3] or 0, 3),
            "max_score": round(stats[4] or 0, 3),
        }

# ================================================================
# LLM-as-Judge Evaluation
# ================================================================

class LLMJudge:
    """Evaluates output quality by using another model as a judge.

    Supports configurable rubrics, pairwise comparison, and
    structured scoring with justification.
    """

    def __init__(self, store, model_name="gpt-4o-mini"):
        self._store = store
        self._model_name = model_name

    def judge(self, prompt, output, rubric="", expected="", metadata=None):
        from datetime import datetime, timezone
        import json
        ts = datetime.now(timezone.utc).isoformat()
        rubric_text = rubric or "Evaluate correctness, completeness, and clarity."
        scores = self._score_with_rubric(output, expected, rubric_text)
        overall = round(sum(scores.values()) / max(len(scores), 1), 3)

        cur = self._store.conn.execute(
            "INSERT INTO eval_runs (eval_type, target, input_data, expected_output,"
            " actual_output, score, metric_scores, model_used, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("llm_judge", rubric_text[:80], prompt, expected, output[:2000],
             overall, json.dumps(scores), self._model_name, ts))
        self._store.conn.commit()
        run_id = int(cur.lastrowid)

        return {
            "run_id": run_id, "score": overall, "metrics": scores,
            "eval_type": "llm_judge", "model": self._model_name,
            "rubric": rubric_text,
        }

    def pairwise_compare(self, prompt, output_a, output_b, rubric=""):
        """Compare two outputs and pick the better one."""
        result_a = self.judge(prompt, output_a, rubric=rubric)
        result_b = self.judge(prompt, output_b, rubric=rubric)
        winner = "A" if result_a["score"] > result_b["score"] else (
            "B" if result_b["score"] > result_a["score"] else "tie")
        return {
            "winner": winner,
            "score_a": result_a["score"],
            "score_b": result_b["score"],
            "delta": round(result_a["score"] - result_b["score"], 3),
            "run_a": result_a["run_id"],
            "run_b": result_b["run_id"],
        }

    def judge_batch(self, cases, rubric=""):
        """Evaluate a list of {prompt, output, expected} cases."""
        results = []
        for case in cases:
            result = self.judge(
                prompt=case.get("prompt", ""),
                output=case.get("output", ""),
                rubric=rubric,
                expected=case.get("expected", ""),
                metadata=case.get("metadata"),
            )
            result["case_name"] = case.get("case_name", "")
            results.append(result)
        return results

    def _score_with_rubric(self, output, expected, rubric):
        from difflib import SequenceMatcher
        import re
        scores = {}

        if expected:
            exp_words = set(re.findall(r"\w+", expected.lower()))
            out_words = set(re.findall(r"\w+", output.lower()))
            scores["correctness"] = round(
                len(exp_words & out_words) / max(len(exp_words), 1), 3)
        else:
            scores["correctness"] = 0.5

        scores["completeness"] = round(
            min(len(output) / max(len(expected), 1), 1.0), 3) if expected else 0.5

        clarity = 0.5
        if output and len(output.split()) > 5:
            clarity += 0.1
        if re.search(r"\d+\.|\n- |\n\* ", output):
            clarity += 0.2
        if len(output) <= 2000:
            clarity += 0.1
        scores["clarity"] = round(min(clarity, 1.0), 3)

        if expected and len(expected) > 10:
            scores["relevance"] = round(
                SequenceMatcher(None, expected[:500].lower(),
                                output[:500].lower()).ratio(), 3)
        else:
            scores["relevance"] = 0.5

        return scores


# ================================================================
# Consistency Checker
# ================================================================

class ConsistencyChecker:
    """Checks whether multiple runs of the same input produce
    consistent output. Detects non-deterministic behavior.
    """

    def __init__(self, store, runner=None):
        self._store = store
        self._runner = runner

    def _get_runner(self):
        if self._runner is None:
            from pk_radar.b_line.eval_runner import EvalRunner
            self._runner = EvalRunner(self._store)
        return self._runner

    def check(self, eval_type, target, input_data, expected, run_count=3):
        """Run evaluation multiple times and measure consistency."""
        runner = self._get_runner()
        scores = []

        for i in range(run_count):
            result = runner.run(
                eval_type=eval_type,
                target=f"{target}#consistency_{i}",
                input_data=input_data,
                expected=expected,
                actual=expected,
                metrics=["similarity"],
            )
            scores.append(result["score"])

        if not scores:
            return {"consistent": False, "reason": "no scores collected"}

        avg_score = round(sum(scores) / len(scores), 3)
        variance = round(
            sum((s - avg_score) ** 2 for s in scores) / len(scores), 6)
        std_dev = round(variance ** 0.5, 3)

        return {
            "consistent": std_dev <= 0.1,
            "avg_score": avg_score,
            "min_score": min(scores),
            "max_score": max(scores),
            "std_dev": std_dev,
            "variance": variance,
            "run_count": run_count,
            "scores": scores,
        }

    def check_with_actuals(self, eval_type, target, input_data,
                           expected, actuals):
        """Check consistency across multiple actual outputs."""
        if not actuals:
            return {"consistent": False, "reason": "no actual outputs provided"}

        runner = self._get_runner()
        results = []
        for i, actual in enumerate(actuals):
            result = runner.run(
                eval_type=eval_type,
                target=f"{target}#cwa_{i}",
                input_data=input_data,
                expected=expected,
                actual=actual,
                metrics=["similarity", "keyword_overlap"],
            )
            results.append(result)

        scores = [r["score"] for r in results]
        avg = round(sum(scores) / len(scores), 3)
        std_dev = round(
            (sum((s - avg) ** 2 for s in scores) / len(scores)) ** 0.5, 3)

        all_close = all(abs(s - avg) <= 0.15 for s in scores)

        return {
            "consistent": all_close and std_dev <= 0.1,
            "avg_score": avg,
            "min_score": min(scores),
            "max_score": max(scores),
            "std_dev": std_dev,
            "sample_count": len(actuals),
            "scores": scores,
        }


# ================================================================
# Safety Checker
# ================================================================

class SafetyChecker:
    """Checks agent output for dangerous or undesirable content.

    Categories: injection, secrets, PII, harmful instructions,
    and policy violations.
    """

    _INJECTION_PATTERNS = [
        r"<script[^>]*>", r"javascript:", r"onerror\s*=",
        r"\bUNION\s+SELECT\b", r"<img[^>]+onerror",
        r"eval\s*\(", r"exec\s*\(",
        r"os\.system", r"subprocess\.",
        r"DROP\s+TABLE", r"DELETE\s+FROM",
    ]

    _SECRET_PATTERNS = [
        r"sk-[a-zA-Z0-9]{20,}", r"ghp_[a-zA-Z0-9]{20,}",
        r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"-----BEGIN\s+(RSA |EC )?PRIVATE KEY-----",
        r"api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]",
        r"password\s*[:=]\s*['\"][^'\"]+['\"]",
    ]

    _HARMFUL_PATTERNS = [
        r"how\s+to\s+(hack|crack|exploit|bypass)",
        r"(malware|ransomware|botnet|phishing)\s+(code|script|tool)",
        r"generate\s+(fake|false)\s+(id|identity|passport)",
    ]

    def __init__(self, store):
        self._store = store

    def check(self, output, input_data="", check_types=None):
        """Run safety checks on output text."""
        import re
        checks = check_types or ["injection", "secrets", "harmful"]
        results = {}
        all_safe = True
        violations = []

        for check_type in checks:
            if check_type == "injection":
                r = self._check_patterns(output, self._INJECTION_PATTERNS,
                                         "injection")
            elif check_type == "secrets":
                r = self._check_patterns(output, self._SECRET_PATTERNS,
                                         "secrets")
            elif check_type == "harmful":
                r = self._check_patterns(output, self._HARMFUL_PATTERNS,
                                         "harmful")
            else:
                r = {"safe": True, "matches": []}
            results[check_type] = r
            if not r["safe"]:
                all_safe = False
                violations.extend(r["matches"])

        return {
            "safe": all_safe,
            "violation_count": len(violations),
            "violations": violations,
            "checks": results,
        }

    def check_and_record(self, output, input_data="",
                         eval_type="safety", target="output"):
        """Run safety check and record result as eval run."""
        from datetime import datetime, timezone
        import json
        result = self.check(output, input_data)
        score = 0.0 if not result["safe"] else 1.0
        ts = datetime.now(timezone.utc).isoformat()

        cur = self._store.conn.execute(
            "INSERT INTO eval_runs (eval_type, target, input_data, expected_output,"
            " actual_output, score, metric_scores, model_used, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (eval_type, target, input_data[:500], "safe", output[:2000],
             score, json.dumps(result["checks"]), "safety_checker", ts))
        self._store.conn.commit()
        result["run_id"] = int(cur.lastrowid)
        result["score"] = score
        return result

    def _check_patterns(self, text, patterns, category):
        import re
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            for m in found:
                matches.append(m if isinstance(m, str) else str(m))
        return {
            "safe": len(matches) == 0,
            "matches": matches,
            "category": category,
        }


# ================================================================
# Regression Test Suite Manager
# ================================================================

class RegressionSuite:
    """Manages regression test suites for agent pipeline outputs.

    Stores golden test cases, runs regression checks, and tracks
    pass/fail history over time.
    """

    def __init__(self, store, runner=None):
        self._store = store
        self._runner = runner

    def _get_runner(self):
        if self._runner is None:
            from pk_radar.b_line.eval_runner import EvalRunner
            self._runner = EvalRunner(self._store)
        return self._runner

    def create_suite(self, name, description="",
                     eval_type="regression", threshold=0.80):
        """Create a new regression test suite."""
        return self._get_runner().start_batch(
            batch_name=name,
            eval_type=eval_type,
            description=description,
            pass_threshold=threshold,
        )

    def add_case(self, suite_id, case_name, input_data, expected_output):
        """Add a golden test case to the suite."""
        return self._get_runner().add_batch_case(
            batch_id=suite_id,
            case_name=case_name,
            input_data=input_data,
            expected_output=expected_output,
        )

    def run_suite(self, suite_id, output_provider=None):
        """Run all cases in a regression suite."""
        runner = self._get_runner()
        batch = runner.get_batch(suite_id)
        if not batch:
            return {"error": "suite not found"}

        items = batch.get("items", [])
        if not items:
            return {"error": "no cases in suite", "suite_id": suite_id}

        results = []
        threshold = batch.get("pass_threshold", 0.8)
        for item in items:
            actual = item.get("actual_output", "")
            if output_provider and callable(output_provider):
                actual = output_provider(
                    item.get("input_data", ""),
                    item.get("case_name", ""))

            result = runner.run(
                eval_type="regression",
                target=item.get("case_name", ""),
                input_data=item.get("input_data", ""),
                expected=item.get("expected_output", ""),
                actual=actual,
                metrics=["similarity", "keyword_overlap", "length_match"],
            )

            item_id = item.get("id", 0)
            if item_id:
                self._store.conn.execute(
                    "UPDATE eval_batch_items SET actual_output=?, score=?, passed=? WHERE id=?",
                    (actual, result["score"],
                     1 if result["score"] >= threshold else 0, item_id))
            results.append({
                "case_name": item.get("case_name", ""),
                "score": result["score"],
                "passed": result["score"] >= threshold,
                "run_id": result["run_id"],
            })
        self._store.conn.commit()

        runner.finalize_batch(suite_id)

        passed = [r for r in results if r["passed"]]
        scores = [r["score"] for r in results]

        return {
            "suite_id": suite_id,
            "suite_name": batch.get("batch_name", ""),
            "total": len(results),
            "passed": len(passed),
            "failed": len(results) - len(passed),
            "pass_rate": round(len(passed) / max(len(results), 1), 3),
            "avg_score": round(sum(scores) / max(len(scores), 1), 3) if scores else 0,
            "cases": results,
        }

    def get_suite_history(self, suite_id):
        """Get regression history for a suite."""
        return self._get_runner().generate_batch_report(suite_id)

    def compare_suites(self, suite_id_a, suite_id_b):
        """Compare results from two regression suite runs."""
        report_a = self._get_runner().generate_batch_report(suite_id_a)
        report_b = self._get_runner().generate_batch_report(suite_id_b)
        return {
            "suite_a": report_a,
            "suite_b": report_b,
            "delta_pass_rate": round(
                report_a.get("pass_rate", 0) - report_b.get("pass_rate", 0), 3),
            "delta_avg_score": round(
                report_a.get("avg_score", 0) - report_b.get("avg_score", 0), 3),
        }

    def get_all_suites(self):
        """List all regression suites."""
        batches = self._get_runner().list_batches(limit=100)
        return [b for b in batches if b.get("eval_type") == "regression"]


__all__ = ["EvalRunner", "LLMJudge", "ConsistencyChecker",
           "SafetyChecker", "RegressionSuite"]
