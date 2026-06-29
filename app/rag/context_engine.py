from __future__ import annotations

from app.core.text import lexical_terms
from app.schemas import ContextPack, CoreObject


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


def summarize_items(items: list[CoreObject], max_chars_per_item: int = 200) -> str:
    if not items:
        return 'No prior memory found.'

    snippets = []
    for index, item in enumerate(items, start=1):
        source = item.source or 'unknown'
        preview = ' '.join(item.content.split())[:max_chars_per_item]
        snippets.append(f'[{index}] {source}: {preview}')
    return '\n'.join(snippets)


def _quality_score(item: CoreObject) -> float:
    value = item.metadata.get('quality_score')
    if isinstance(value, (int, float)):
        return max(0.0, min(float(value), 1.0))
    return 0.5


def score_context(query: str, items: list[CoreObject], top_k: int) -> tuple[float, list[str]]:
    if not items:
        return 0.0, ['no matching memory found']

    query_terms = lexical_terms(query)
    combined_terms = set()
    estimated_tokens = estimate_tokens(query)
    quality_scores = []

    for item in items:
        combined_terms.update(lexical_terms(item.content))
        estimated_tokens += estimate_tokens(item.content[:400])
        quality_scores.append(_quality_score(item))

    item_count_signal = min(len(items) / max(top_k, 1), 1.0)
    overlap_signal = 0.0
    if query_terms:
        overlap_signal = len(query_terms & combined_terms) / len(query_terms)
    source_signal = 1.0 if any((item.source or 'unknown') != 'unknown' for item in items) else 0.0
    quality_signal = sum(quality_scores) / max(len(quality_scores), 1)

    score = (
        item_count_signal * 0.25
        + overlap_signal * 0.40
        + source_signal * 0.15
        + quality_signal * 0.20
    )
    score = round(min(score, 1.0), 3)

    reasons = [
        f'item_count={len(items)}/{top_k}',
        f'query_term_overlap={overlap_signal:.2f}',
        f'source_presence={source_signal:.2f}',
        f'quality_signal={quality_signal:.2f}',
        f'estimated_tokens={estimated_tokens}',
    ]
    return score, reasons


def build_context_pack(query: str, items: list[CoreObject], top_k: int = 5) -> ContextPack:
    summary = summarize_items(items)
    score, reasons = score_context(query, items, top_k)
    return ContextPack(query=query, items=items, summary=summary, score=score, score_reasons=reasons)
