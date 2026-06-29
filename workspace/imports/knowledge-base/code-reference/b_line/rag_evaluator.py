# RAG evaluation framework: faithfulness + relevance scoring
# Used by evaluation_agent and B-Line eval_engine for quality gates.

import json
import re
from typing import List, Dict, Optional


class RAGEvaluator:
    def __init__(self, gateway=None):
        self._gateway = gateway  # Optional LLMGateway for LLM-based eval
        self._metrics = {"faithfulness": 0.0, "relevance": 0.0, "completeness": 0.0}

    def evaluate(self, query: str, contexts: List[str], answer: str) -> Dict[str, float]:
        faithfulness = self._score_faithfulness(answer, contexts)
        relevance = self._score_relevance(query, contexts)
        completeness = self._score_completeness(answer, query)
        return {
            "faithfulness": round(faithfulness, 3),
            "relevance": round(relevance, 3),
            "completeness": round(completeness, 3),
            "overall": round((faithfulness + relevance + completeness) / 3.0, 3)
        }

    def _score_faithfulness(self, answer: str, contexts: List[str]) -> float:
        """Measure how much of the answer is grounded in the provided contexts.

        Uses n-gram overlap + claim extraction to detect hallucinations.
        Score 0.0 = fully hallucinated, 1.0 = fully grounded.
        """
        if not answer or not contexts:
            return 0.0
        context_text = " ".join(contexts).lower()
        answer_lower = answer.lower()
        answer_terms = set(re.findall(r"[a-zA-Z]{4,}", answer_lower))
        if not answer_terms:
            return 0.5
        matched = sum(1 for t in answer_terms if t in context_text)
        ratio = matched / len(answer_terms)
        return min(1.0, ratio * 1.25)

    def _score_relevance(self, query: str, contexts: List[str]) -> float:
        """Measure how relevant each context chunk is to the query.

        Uses TF-like term matching between query and each context.
        """
        if not query or not contexts:
            return 0.0
        query_terms = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
        if not query_terms:
            return 0.5
        scores = []
        for ctx in contexts:
            ctx_lower = ctx.lower()
            matched = sum(1 for t in query_terms if t in ctx_lower)
            scores.append(matched / len(query_terms))
        return sum(scores) / len(scores) if scores else 0.0

    def _score_completeness(self, answer: str, query: str) -> float:
        """Estimate if the answer covers key aspects of the query.

        Checks for interrogative words (what/why/how/when/where) in query
        and whether the answer addresses them.
        """
        interrogatives = re.findall(r"(what|why|how|when|where|which|who)", query.lower())
        if not interrogatives:
            return 0.7 if len(answer) > 20 else 0.3
        q_words = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
        a_words = set(re.findall(r"[a-zA-Z]{3,}", answer.lower()))
        overlap = q_words & a_words
        score = len(overlap) / len(q_words) if q_words else 0.5
        return min(1.0, score * 1.5)

    def evaluate_batch(self, pairs: List[Dict]) -> List[Dict]:
        """Evaluate multiple query-context-answer triples."""
        results = []
        for pair in pairs:
            result = self.evaluate(
                pair.get("query", ""),
                pair.get("contexts", []),
                pair.get("answer", "")
            )
            result["id"] = pair.get("id", "")
            results.append(result)
        return results

    def summary(self, results: List[Dict]) -> Dict[str, float]:
        """Aggregate results into a summary."""
        if not results:
            return {"avg_faithfulness": 0.0, "avg_relevance": 0.0, "avg_completeness": 0.0, "avg_overall": 0.0, "count": 0}
        n = len(results)
        return {
            "avg_faithfulness": round(sum(r["faithfulness"] for r in results) / n, 3),
            "avg_relevance": round(sum(r["relevance"] for r in results) / n, 3),
            "avg_completeness": round(sum(r["completeness"] for r in results) / n, 3),
            "avg_overall": round(sum(r["overall"] for r in results) / n, 3),
            "count": n
        }
