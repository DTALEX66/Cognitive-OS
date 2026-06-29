from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.text import lexical_terms

BLOCKED_PATTERNS = [
    r'access denied',
    r'captcha',
    r'verify.*human',
    r'blocked',
    r'rate limit',
    r'too many requests',
    r'please.*try again',
    r'503.*service.*unavailable',
    r'访问被拒绝',
    r'验证码',
    r'请验证',
    r'请求过多',
]


@dataclass(frozen=True)
class ContentQuality:
    score: float
    issues: list[str]
    looks_blocked: bool = False

    @property
    def is_low_quality(self) -> bool:
        return self.score < 0.5

    def metadata(self) -> dict[str, object]:
        return {
            'quality_score': round(self.score, 3),
            'quality_issues': self.issues,
            'looks_blocked': self.looks_blocked,
        }

    def compact_report(self) -> str:
        issue_text = ','.join(self.issues) if self.issues else 'none'
        return f'quality={self.score:.2f}; blocked={self.looks_blocked}; issues={issue_text}'


def assess_content_quality(content: str, source_type: str = 'text') -> ContentQuality:
    text = content or ''
    stripped = text.strip()
    lowered = stripped.lower()
    issues: list[str] = []
    score = 1.0

    if not stripped:
        issues.append('empty_content')
        score -= 1.0
    elif len(stripped) < 10:
        issues.append('content_too_short')
        score -= 0.30

    if source_type == 'web' and len(stripped) > 100_000:
        issues.append('excessive_length')
        score -= 0.10

    looks_blocked = any(re.search(pattern, lowered) for pattern in BLOCKED_PATTERNS)
    if looks_blocked:
        issues.append('looks_blocked')
        score -= 0.50

    terms = lexical_terms(stripped)
    if stripped and len(terms) <= 1 and len(stripped) > 20:
        issues.append('low_term_diversity')
        score -= 0.20

    if 200 <= len(stripped) <= 50_000:
        score += 0.10

    return ContentQuality(score=max(0.0, min(1.0, score)), issues=issues, looks_blocked=looks_blocked)
