"""B-Line Machine Lesson - Experience extraction and pattern recognition.

Extracts lessons from execution traces and evaluation results,
identifies patterns (success and failure), and feeds them back
into the routing engine to improve future decisions.
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
import json
import re


class MachineLessonEngine:
    """Extracts and applies lessons from B-line execution experience.

    Monitors execution traces and evaluation runs to:
    - Identify recurring success and failure patterns
    - Extract actionable lessons with confidence scores
    - Feed lessons back into machine routes
    - Track lesson effectiveness over time
    """

    def __init__(self, store: Any) -> None:
        self._store = store

    # ── Lesson CRUD ──

    def create_lesson(self, title: str, lesson_type: str = "pattern",
                      category: str = "general",
                      trigger_condition: str = "",
                      recommended_action: str = "",
                      source_trace_ids: list[int] | None = None,
                      source_eval_ids: list[int] | None = None,
                      confidence: float = 0.5) -> int:
        ts = datetime.now(timezone.utc).isoformat()
        cur = self._store.conn.execute(
            "INSERT INTO machine_lessons (title, lesson_type, category,"
            " trigger_condition, recommended_action, source_trace_ids,"
            " source_eval_ids, success_count, failure_count, confidence,"
            " impact_score, applied_count, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, ?, 0, 0, ?, ?)",
            (title, lesson_type, category, trigger_condition, recommended_action,
             json.dumps(source_trace_ids or []),
             json.dumps(source_eval_ids or []),
             confidence, ts, ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def get_lesson(self, lesson_id: int) -> dict | None:
        row = self._store.conn.execute(
            "SELECT * FROM machine_lessons WHERE id=?", (lesson_id,)).fetchone()
        if not row:
            return None
        r = dict(row)
        r["source_trace_ids"] = json.loads(r.get("source_trace_ids", "[]"))
        r["source_eval_ids"] = json.loads(r.get("source_eval_ids", "[]"))
        return r

    def update_lesson(self, lesson_id: int, **kwargs) -> bool:
        existing = self.get_lesson(lesson_id)
        if not existing:
            return False
        updates = {}
        simple_fields = ["title", "lesson_type", "category", "trigger_condition",
                         "recommended_action", "confidence", "impact_score"]
        for f in simple_fields:
            if f in kwargs and kwargs[f] is not None:
                updates[f] = kwargs[f]
        for list_field in ["source_trace_ids", "source_eval_ids"]:
            if list_field in kwargs:
                updates[list_field] = json.dumps(kwargs[list_field] or [])
        if not updates:
            return True
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [lesson_id]
        self._store.conn.execute(
            f"UPDATE machine_lessons SET {set_clause} WHERE id=?", values)
        self._store.conn.commit()
        return True

    def delete_lesson(self, lesson_id: int) -> bool:
        existing = self.get_lesson(lesson_id)
        if not existing:
            return False
        self._store.conn.execute("DELETE FROM machine_lessons WHERE id=?", (lesson_id,))
        self._store.conn.commit()
        return True

    def list_lessons(self, lesson_type: str = "", category: str = "",
                     min_confidence: float = 0.0, limit: int = 50) -> list[dict]:
        conditions = []
        params = []
        if lesson_type:
            conditions.append("lesson_type=?")
            params.append(lesson_type)
        if category:
            conditions.append("category=?")
            params.append(category)
        if min_confidence > 0:
            conditions.append("confidence >= ?")
            params.append(min_confidence)
        where = " AND ".join(conditions) if conditions else "1=1"
        cur = self._store.conn.execute(
            f"SELECT * FROM machine_lessons WHERE {where}"
            " ORDER BY confidence DESC, impact_score DESC LIMIT ?",
            params + [limit])
        result = []
        for row in cur.fetchall():
            r = dict(row)
            r["source_trace_ids"] = json.loads(r.get("source_trace_ids", "[]"))
            r["source_eval_ids"] = json.loads(r.get("source_eval_ids", "[]"))
            result.append(r)
        return result

    # ── Pattern Extraction ──

    def extract_from_traces(self, limit: int = 100) -> list[dict]:
        """Analyze recent execution traces to identify patterns and auto-create lessons."""
        traces = self._store.conn.execute(
            "SELECT * FROM execution_traces ORDER BY created_at DESC LIMIT ?",
            (limit,)).fetchall()

        if not traces:
            return []

        # Group by tool_name and success/failure
        tool_stats: dict[str, dict] = {}
        for t in traces:
            trace = dict(t)
            tool = trace.get("tool_name", "unknown")
            if tool not in tool_stats:
                tool_stats[tool] = {"total": 0, "successes": 0, "failures": 0, "durations": []}
            stats = tool_stats[tool]
            stats["total"] += 1
            if trace.get("success"):
                stats["successes"] += 1
            else:
                stats["failures"] += 1
            dur = trace.get("duration_ms", 0)
            if dur > 0:
                stats["durations"].append(dur)

        results = []
        for tool, stats in tool_stats.items():
            fail_rate = stats["failures"] / max(stats["total"], 1)
            avg_dur = sum(stats["durations"]) / max(len(stats["durations"]), 1) if stats["durations"] else 0

            # High failure rate -> anti-pattern lesson
            if fail_rate > 0.3 and stats["total"] >= 3:
                trace_ids = [dict(t)["id"] for t in traces if dict(t).get("tool_name") == tool]
                lesson_id = self.create_lesson(
                    title=f"High failure rate for {tool}",
                    lesson_type="anti_pattern",
                    category="reliability",
                    trigger_condition=f"tool == '{tool}'",
                    recommended_action=f"Review {tool} usage; {fail_rate:.0%} failure rate over {stats['total']} calls",
                    source_trace_ids=trace_ids[:10],
                    confidence=min(fail_rate + 0.2, 0.95),
                )
                results.append({
                    "tool": tool, "type": "anti_pattern",
                    "fail_rate": round(fail_rate, 3),
                    "lesson_id": lesson_id,
                })

            # Very high success -> success pattern
            if fail_rate < 0.1 and stats["total"] >= 5:
                trace_ids = [dict(t)["id"] for t in traces if dict(t).get("tool_name") == tool]
                lesson_id = self.create_lesson(
                    title=f"Reliable pattern for {tool}",
                    lesson_type="success_pattern",
                    category="best_practice",
                    trigger_condition=f"tool == '{tool}'",
                    recommended_action=f"Continue using {tool} as is; {100 - fail_rate:.0f}% success rate",
                    source_trace_ids=trace_ids[:10],
                    confidence=0.85,
                )
                results.append({
                    "tool": tool, "type": "success_pattern",
                    "success_rate": round(1 - fail_rate, 3),
                    "lesson_id": lesson_id,
                })

            # Slow tool detection
            if avg_dur > 5000 and stats["total"] >= 2:
                lesson_id = self.create_lesson(
                    title=f"Slow tool detected: {tool}",
                    lesson_type="performance",
                    category="performance",
                    trigger_condition=f"tool == '{tool}'",
                    recommended_action=f"Consider optimization; avg {avg_dur:.0f}ms over {stats['total']} calls",
                    source_trace_ids=[dict(t)["id"] for t in traces if dict(t).get("tool_name") == tool][:5],
                    confidence=0.7,
                )
                results.append({
                    "tool": tool, "type": "performance",
                    "avg_duration_ms": round(avg_dur, 0),
                    "lesson_id": lesson_id,
                })

        return results

    def extract_from_evals(self, min_runs: int = 3, low_score_threshold: float = 0.5) -> list[dict]:
        """Analyze evaluation runs to find quality issues and create lessons."""
        rows = self._store.conn.execute(
            "SELECT eval_type, target, COUNT(*) as cnt, AVG(score) as avg_score"
            " FROM eval_runs GROUP BY eval_type, target HAVING cnt >= ?"
            " ORDER BY avg_score ASC", (min_runs,)).fetchall()

        results = []
        for row in rows:
            eval_type, target, cnt, avg_score = row
            if avg_score < low_score_threshold:
                eval_ids = self._store.conn.execute(
                    "SELECT id FROM eval_runs WHERE eval_type=? AND target=?",
                    (eval_type, target)).fetchall()
                eval_id_list = [r[0] for r in eval_ids]
                lesson_id = self.create_lesson(
                    title=f"Low quality: {target} ({eval_type})",
                    lesson_type="quality_issue",
                    category="quality",
                    trigger_condition=f"eval_target == '{target}' AND eval_type == '{eval_type}'",
                    recommended_action=f"Improve {target} output quality; avg score {avg_score:.2f} over {cnt} runs",
                    source_eval_ids=eval_id_list[:10],
                    confidence=min((1 - avg_score) + 0.3, 0.9),
                )
                results.append({
                    "eval_type": eval_type, "target": target,
                    "avg_score": round(avg_score, 3), "runs": cnt,
                    "lesson_id": lesson_id,
                })

        return results

    # ── Feedback to Routes ──

    def apply_lesson_to_route(self, lesson_id: int, route_id: int) -> dict:
        """Link a lesson to a route so it influences future routing decisions."""
        lesson = self.get_lesson(lesson_id)
        if not lesson:
            return {"error": "lesson not found"}

        route = self._store.conn.execute(
            "SELECT * FROM machine_routes WHERE id=?", (route_id,)).fetchone()
        if not route:
            return {"error": "route not found"}

        ts = datetime.now(timezone.utc).isoformat()

        # Check for existing link
        existing = self._store.conn.execute(
            "SELECT id FROM lesson_route_links WHERE lesson_id=? AND route_id=?",
            (lesson_id, route_id)).fetchone()
        if existing:
            self._store.conn.execute(
                "UPDATE lesson_route_links SET applied_at=? WHERE id=?",
                (ts, existing[0]))
        else:
            effect = "boost" if lesson.get("lesson_type", "").startswith("success") else "warn"
            self._store.conn.execute(
                "INSERT INTO lesson_route_links (lesson_id, route_id, effect, applied_at)"
                " VALUES (?, ?, ?, ?)", (lesson_id, route_id, effect, ts))

        # Update applied count
        self._store.conn.execute(
            "UPDATE machine_lessons SET applied_count = applied_count + 1,"
            " last_applied_at = ?, updated_at = ? WHERE id = ?",
            (ts, ts, lesson_id))
        self._store.conn.commit()

        return {
            "status": "applied",
            "lesson_id": lesson_id,
            "route_id": route_id,
            "lesson_title": lesson["title"],
        }

    def get_lessons_for_route(self, route_id: int) -> list[dict]:
        cur = self._store.conn.execute(
            "SELECT ml.*, lrl.effect, lrl.applied_at as link_applied_at"
            " FROM machine_lessons ml"
            " JOIN lesson_route_links lrl ON ml.id = lrl.lesson_id"
            " WHERE lrl.route_id = ? ORDER BY lrl.applied_at DESC",
            (route_id,))
        result = []
        for row in cur.fetchall():
            r = dict(row)
            r["source_trace_ids"] = json.loads(r.get("source_trace_ids", "[]"))
            r["source_eval_ids"] = json.loads(r.get("source_eval_ids", "[]"))
            result.append(r)
        return result

    def find_matching_lessons(self, goal: str, tool_name: str = "",
                              eval_type: str = "") -> list[dict]:
        """Find lessons that match the current execution context."""
        all_lessons = self.list_lessons(min_confidence=0.3)
        matches = []
        goal_lower = goal.lower()

        for lesson in all_lessons:
            score = 0.0
            trigger = lesson.get("trigger_condition", "").lower()

            if tool_name and tool_name.lower() in trigger:
                score += 30.0
            if eval_type and eval_type.lower() in trigger:
                score += 20.0

            # Keyword overlap with goal
            trigger_words = set(re.findall(r'w+', trigger))
            goal_words = set(re.findall(r'w+', goal_lower))
            overlap = trigger_words & goal_words
            if overlap:
                score += len(overlap) * 10.0

            # Category relevance
            category = lesson.get("category", "")
            if category and category in goal_lower:
                score += 15.0

            if score > 5.0:
                lesson["match_score"] = round(score, 2)
                matches.append(lesson)

        matches.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return matches[:10]

    # ── Lesson Impact Tracking ──

    def record_lesson_success(self, lesson_id: int) -> None:
        self._store.conn.execute(
            "UPDATE machine_lessons SET success_count = success_count + 1,"
            " updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), lesson_id))
        self._store.conn.commit()
        self._recalc_impact(lesson_id)

    def record_lesson_failure(self, lesson_id: int) -> None:
        self._store.conn.execute(
            "UPDATE machine_lessons SET failure_count = failure_count + 1,"
            " updated_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), lesson_id))
        self._store.conn.commit()
        self._recalc_impact(lesson_id)

    def _recalc_impact(self, lesson_id: int) -> None:
        row = self._store.conn.execute(
            "SELECT success_count, failure_count, applied_count, confidence"
            " FROM machine_lessons WHERE id=?", (lesson_id,)).fetchone()
        if not row:
            return
        success, failure, applied, confidence = row
        total = success + failure
        if total > 0 and applied > 0:
            impact = (success / total) * confidence * min(applied / 10, 1.0)
            self._store.conn.execute(
                "UPDATE machine_lessons SET impact_score = ? WHERE id = ?",
                (round(impact, 3), lesson_id))
            self._store.conn.commit()

    def get_high_impact_lessons(self, min_impact: float = 0.5, limit: int = 20) -> list[dict]:
        cur = self._store.conn.execute(
            "SELECT * FROM machine_lessons WHERE impact_score >= ?"
            " ORDER BY impact_score DESC LIMIT ?", (min_impact, limit))
        result = []
        for row in cur.fetchall():
            r = dict(row)
            r["source_trace_ids"] = json.loads(r.get("source_trace_ids", "[]"))
            r["source_eval_ids"] = json.loads(r.get("source_eval_ids", "[]"))
            result.append(r)
        return result

    def get_lesson_stats(self) -> dict:
        total = self._store.conn.execute(
            "SELECT COUNT(*) FROM machine_lessons").fetchone()[0] or 0
        by_type = self._store.conn.execute(
            "SELECT lesson_type, COUNT(*) FROM machine_lessons"
            " GROUP BY lesson_type ORDER BY COUNT(*) DESC").fetchall()
        total_applied = self._store.conn.execute(
            "SELECT SUM(applied_count) FROM machine_lessons").fetchone()[0] or 0
        avg_confidence = self._store.conn.execute(
            "SELECT AVG(confidence) FROM machine_lessons").fetchone()[0] or 0
        return {
            "total_lessons": total,
            "by_type": [{"type": r[0], "count": r[1]} for r in by_type],
            "total_applications": total_applied,
            "avg_confidence": round(avg_confidence, 3),
        }

# ================================================================
# Lesson Extractor - Auto-extract lessons from eval results
# ================================================================

class LessonExtractor:
    """Automatically extracts lessons from evaluation results and
    execution traces.

    Analyzes eval runs, batch results, and trace data to identify
    patterns worth encoding as machine lessons.
    """

    def __init__(self, store, engine=None):
        self._store = store
        self._engine = engine

    def _get_engine(self):
        if self._engine is None:
            from pk_radar.b_line.machine_lesson import MachineLessonEngine
            self._engine = MachineLessonEngine(self._store)
        return self._engine

    def extract_from_evals(self, eval_type="", min_score=0.0,
                           max_score=1.0, limit=50):
        """Extract lessons from evaluation runs."""
        import json

        if eval_type:
            cur = self._store.conn.execute(
                "SELECT * FROM eval_runs WHERE eval_type=? AND score BETWEEN ? AND ?"
                " ORDER BY created_at DESC LIMIT ?",
                (eval_type, min_score, max_score, limit))
        else:
            cur = self._store.conn.execute(
                "SELECT * FROM eval_runs WHERE score BETWEEN ? AND ?"
                " ORDER BY created_at DESC LIMIT ?",
                (min_score, max_score, limit))

        lessons = []
        for row in cur.fetchall():
            r = dict(row)
            metric_scores = json.loads(r.get("metric_scores", "{}"))
            target = r.get("target", "")
            score = r.get("score", 0)

            if score >= 0.8:
                lessons.append({
                    "title": f"High-score pattern: {target[:60]}",
                    "lesson_type": "success_pattern",
                    "category": r.get("eval_type", "general"),
                    "trigger_condition": f"target contains '{target[:40]}'",
                    "recommended_action": f"Reuse approach from eval #{r['id']}",
                    "confidence": min(score, 0.95),
                    "source_eval_ids": [r["id"]],
                })
            elif score <= 0.3:
                lessons.append({
                    "title": f"Low-score pattern: {target[:60]}",
                    "lesson_type": "failure_pattern",
                    "category": r.get("eval_type", "general"),
                    "trigger_condition": f"target contains '{target[:40]}'",
                    "recommended_action": f"Avoid approach from eval #{r['id']}",
                    "confidence": min(1.0 - score, 0.85),
                    "source_eval_ids": [r["id"]],
                })

        return lessons

    def extract_from_batches(self, limit=20):
        """Extract lessons from batch evaluation results."""
        cur = self._store.conn.execute(
            "SELECT * FROM eval_batches ORDER BY created_at DESC LIMIT ?",
            (limit,))
        lessons = []
        for row in cur.fetchall():
            r = dict(row)
            batch_name = r.get("batch_name", "")
            pass_rate = r.get("passed_cases", 0) / max(r.get("total_cases", 1), 1)
            avg_score = r.get("avg_score", 0)

            if pass_rate >= 0.9 and avg_score >= 0.8:
                lessons.append({
                    "title": f"Reliable batch: {batch_name[:60]}",
                    "lesson_type": "success_pattern",
                    "category": r.get("eval_type", "general"),
                    "trigger_condition": f"batch '{batch_name[:40]}'",
                    "recommended_action": "Use this batch configuration as template",
                    "confidence": min(avg_score, 0.95),
                })
            elif pass_rate <= 0.3 and r.get("total_cases", 0) >= 5:
                lessons.append({
                    "title": f"Problematic batch: {batch_name[:60]}",
                    "lesson_type": "failure_pattern",
                    "category": r.get("eval_type", "general"),
                    "trigger_condition": f"batch '{batch_name[:40]}'",
                    "recommended_action": "Review test cases quality and thresholds",
                    "confidence": min(1.0 - pass_rate, 0.8),
                })

        return lessons

    def extract_and_save(self, eval_type="", min_score=0.0,
                         max_score=1.0, limit=50):
        """Extract lessons and persist them to the database."""
        engine = self._get_engine()
        lessons = self.extract_from_evals(
            eval_type=eval_type, min_score=min_score,
            max_score=max_score, limit=limit)
        batches = self.extract_from_batches(limit=20)
        all_lessons = lessons + batches

        created_ids = []
        for lesson in all_lessons:
            lid = engine.create_lesson(
                title=lesson["title"],
                lesson_type=lesson.get("lesson_type", "pattern"),
                category=lesson.get("category", "general"),
                trigger_condition=lesson.get("trigger_condition", ""),
                recommended_action=lesson.get("recommended_action", ""),
                source_eval_ids=lesson.get("source_eval_ids", []),
                confidence=lesson.get("confidence", 0.5),
            )
            created_ids.append(lid)

        return {
            "extracted": len(all_lessons),
            "created_ids": created_ids,
            "from_evals": len(lessons),
            "from_batches": len(batches),
        }


# ================================================================
# Lesson Prioritizer
# ================================================================

class LessonPrioritizer:
    """Prioritizes machine lessons based on impact, confidence,
    recency, and relevance to current goals.
    """

    def __init__(self, store, engine=None):
        self._store = store
        self._engine = engine

    def _get_engine(self):
        if self._engine is None:
            from pk_radar.b_line.machine_lesson import MachineLessonEngine
            self._engine = MachineLessonEngine(self._store)
        return self._engine

    def prioritize(self, goal="", limit=20):
        """Rank lessons by a composite priority score."""
        lessons = self._get_engine().list_lessons(min_confidence=0.2, limit=200)
        scored = []
        goal_lower = goal.lower()

        for lesson in lessons:
            score = self._compute_priority(lesson, goal_lower)
            lesson["priority_score"] = score
            scored.append(lesson)

        scored.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        return scored[:limit]

    def _compute_priority(self, lesson, goal_lower):
        """Compute composite priority score for a lesson."""
        import re
        score = 0.0

        # Impact score (0-1) * 40
        impact = lesson.get("impact_score", 0) or 0
        score += min(impact, 1.0) * 40

        # Confidence (0-1) * 30
        confidence = lesson.get("confidence", 0.5) or 0.5
        score += confidence * 30

        # Success ratio * 15
        success = lesson.get("success_count", 0) or 0
        failure = lesson.get("failure_count", 0) or 0
        total = success + failure
        if total > 0:
            score += (success / total) * 15

        # Recency bonus: applied_count * 5 (capped)
        applied = lesson.get("applied_count", 0) or 0
        score += min(applied, 10) * 0.5

        # Goal relevance: keyword overlap * 10
        trigger = (lesson.get("trigger_condition", "") or "").lower()
        trigger_words = set(re.findall(r"\w+", trigger))
        goal_words = set(re.findall(r"\w+", goal_lower))
        overlap = trigger_words & goal_words
        if overlap:
            score += min(len(overlap) * 3, 10)

        return round(score, 2)

    def get_top_by_category(self, goal="", top_per_category=5):
        """Get top N lessons per category."""
        all_lessons = self._get_engine().list_lessons(
            min_confidence=0.2, limit=200)
        categories = {}
        for lesson in all_lessons:
            cat = lesson.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(lesson)

        result = {}
        goal_lower = goal.lower()
        for cat, lessons in categories.items():
            scored = []
            for l in lessons:
                l["priority_score"] = self._compute_priority(l, goal_lower)
                scored.append(l)
            scored.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            result[cat] = scored[:top_per_category]

        return result


# ================================================================
# Lesson Route Advisor
# ================================================================

class LessonRouteAdvisor:
    """Applies machine lessons to generate route suggestions and
    adjustments for the routing engine.
    """

    def __init__(self, store, engine=None):
        self._store = store
        self._engine = engine

    def _get_engine(self):
        if self._engine is None:
            from pk_radar.b_line.machine_lesson import MachineLessonEngine
            self._engine = MachineLessonEngine(self._store)
        return self._engine

    def suggest_routes(self, goal, tool_name="", max_suggestions=5):
        """Suggest route adjustments based on matching lessons."""
        engine = self._get_engine()
        lessons = engine.find_matching_lessons(
            goal=goal, tool_name=tool_name)

        suggestions = []
        for lesson in lessons[:max_suggestions]:
            suggestion = {
                "lesson_id": lesson["id"],
                "title": lesson.get("title", ""),
                "match_score": lesson.get("match_score", 0),
                "action": lesson.get("recommended_action", ""),
                "confidence": lesson.get("confidence", 0.5),
                "lesson_type": lesson.get("lesson_type", ""),
                "category": lesson.get("category", ""),
            }

            if lesson.get("lesson_type") == "failure_pattern":
                suggestion["advice"] = "avoid"
            elif lesson.get("lesson_type") == "success_pattern":
                suggestion["advice"] = "apply"
            elif lesson.get("lesson_type") == "optimization":
                suggestion["advice"] = "consider"
            else:
                suggestion["advice"] = "review"

            suggestions.append(suggestion)

        return {
            "goal": goal,
            "tool_name": tool_name,
            "suggestions": suggestions,
            "total_matches": len(lessons),
        }

    def apply_best_lesson(self, goal, tool_name="",
                          route_id=None, min_match_score=20):
        """Find and immediately apply the best matching lesson."""
        engine = self._get_engine()
        lessons = engine.find_matching_lessons(
            goal=goal, tool_name=tool_name)

        best = None
        for lesson in lessons:
            if lesson.get("match_score", 0) >= min_match_score:
                best = lesson
                break

        if not best:
            return {"applied": False, "reason": "no suitable lesson found"}

        if route_id:
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).isoformat()
            self._store.conn.execute(
                "INSERT OR IGNORE INTO lesson_route_links"
                " (lesson_id, route_id, effect, applied_at)"
                " VALUES (?, ?, ?, ?)",
                (best["id"], route_id,
                 "positive" if best.get("lesson_type") == "success_pattern" else "warning",
                 ts))
            self._store.conn.commit()

            engine.record_lesson_success(best["id"])

        return {
            "applied": True,
            "lesson_id": best["id"],
            "title": best.get("title", ""),
            "confidence": best.get("confidence", 0),
            "match_score": best.get("match_score", 0),
            "route_id": route_id,
        }


# ================================================================
# A/B Test Runner
# ================================================================

class ABTestRunner:
    """Runs A/B tests comparing old vs new strategies or model
    configurations for agent pipelines.
    """

    def __init__(self, store):
        self._store = store

    def create_test(self, name, control_config, treatment_config,
                    description="", eval_type="ab_test"):
        """Create a new A/B test with control and treatment configs."""
        from datetime import datetime, timezone
        import json
        ts = datetime.now(timezone.utc).isoformat()

        cur = self._store.conn.execute(
            "INSERT INTO eval_batches (batch_name, description, eval_type,"
            " total_cases, passed_cases, avg_score, min_score, max_score,"
            " pass_threshold, status, report_json, created_at)"
            " VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0.7, 'running', ?, ?)",
            (name, description, eval_type,
             json.dumps({"control": control_config, "treatment": treatment_config}),
             ts))
        self._store.conn.commit()
        return int(cur.lastrowid)

    def add_test_case(self, test_id, case_name, input_data,
                      expected_output, control_output, treatment_output):
        """Add a test case with both control and treatment outputs."""
        runner = self._get_runner()
        # Record control
        c_result = runner.run(
            eval_type="ab_test_control",
            target=f"{case_name}#control",
            input_data=input_data,
            expected=expected_output,
            actual=control_output,
            metrics=["similarity", "keyword_overlap", "length_match"],
        )
        # Record treatment
        t_result = runner.run(
            eval_type="ab_test_treatment",
            target=f"{case_name}#treatment",
            input_data=input_data,
            expected=expected_output,
            actual=treatment_output,
            metrics=["similarity", "keyword_overlap", "length_match"],
        )

        item_id = runner.add_batch_item(
            batch_id=test_id,
            case_name=case_name,
            input_data=input_data,
            expected_output=expected_output,
        )
        if item_id:
            self._store.conn.execute(
                "UPDATE eval_batch_items SET actual_output=?, score=? WHERE id=?",
                (control_output, c_result["score"], item_id))
            self._store.conn.commit()

        return {
            "item_id": item_id,
            "control_score": c_result["score"],
            "treatment_score": t_result["score"],
            "delta": round(t_result["score"] - c_result["score"], 3),
            "winner": "treatment" if t_result["score"] > c_result["score"] else (
                "control" if c_result["score"] > t_result["score"] else "tie"),
        }

    def run_test(self, test_id, cases):
        """Run all cases for an A/B test and produce results."""
        runner = self._get_runner()
        batch = runner.get_batch(test_id)
        if not batch:
            return {"error": "test not found"}

        import json
        config = json.loads(batch.get("report_json", "{}"))

        results = []
        for case in cases:
            result = self.add_test_case(
                test_id=test_id,
                case_name=case.get("case_name", ""),
                input_data=case.get("input_data", ""),
                expected_output=case.get("expected_output", ""),
                control_output=case.get("control_output", ""),
                treatment_output=case.get("treatment_output", ""),
            )
            results.append(result)

        runner.finalize_batch(test_id)

        control_scores = [r["control_score"] for r in results]
        treatment_scores = [r["treatment_score"] for r in results]
        treatment_wins = sum(1 for r in results if r["winner"] == "treatment")
        control_wins = sum(1 for r in results if r["winner"] == "control")
        ties = sum(1 for r in results if r["winner"] == "tie")

        return {
            "test_id": test_id,
            "test_name": batch.get("batch_name", ""),
            "config": config,
            "total_cases": len(results),
            "control_avg": round(sum(control_scores) / max(len(control_scores), 1), 3),
            "treatment_avg": round(sum(treatment_scores) / max(len(treatment_scores), 1), 3),
            "control_wins": control_wins,
            "treatment_wins": treatment_wins,
            "ties": ties,
            "recommendation": "treatment" if treatment_wins > control_wins else (
                "control" if control_wins > treatment_wins else "inconclusive"),
            "cases": results,
        }

    def get_test_results(self, test_id):
        """Get results for a completed A/B test."""
        return self._get_runner().get_batch(test_id)

    def list_tests(self, limit=20):
        """List all A/B tests."""
        batches = self._get_runner().list_batches(limit=limit)
        return [b for b in batches if b.get("eval_type") == "ab_test"]

    def _get_runner(self):
        from pk_radar.b_line.eval_runner import EvalRunner
        return EvalRunner(self._store)


__all__ = ["MachineLessonEngine", "LessonExtractor", "LessonPrioritizer",
           "LessonRouteAdvisor", "ABTestRunner"]
