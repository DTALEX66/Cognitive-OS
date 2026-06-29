"""Content quality assessment for A-Line."""
import re

BLOCKED_PATTERNS = [
    r"access denied", r"captcha", r"verify.*human",
    r"blocked", r"rate limit", r"too many requests",
    r"please.*try again", r"503.*service.*unavailable",
]


class ContentQuality:
    def __init__(self, score=0.5, issues=None, looks_blocked=False):
        self.score = score
        self.issues = issues or []
        self.looks_blocked = looks_blocked
        self.is_low_quality = score < 0.5

    def compact_report(self) -> str:
        return f"score={self.score:.2f}, blocked={self.looks_blocked}, issues={len(self.issues)}"


def assess_content_quality(content, source_type="text"):
    issues = []
    score = 1.0
    text = content or ""
    if len(text.strip()) < 10:
        issues.append("content_too_short")
        score -= 0.3
    if source_type == "web" and len(text) > 100000:
        issues.append("excessive_length")
        score -= 0.1
    looks_blocked = any(re.search(p, text.lower()) for p in BLOCKED_PATTERNS)
    if looks_blocked:
        issues.append("looks_blocked")
        score -= 0.5
    words = re.findall(r"\w+", text.lower())
    if words:
        unique_ratio = len(set(words)) / max(len(words), 1)
        if unique_ratio < 0.3:
            issues.append("low_diversity")
            score -= 0.1
    length = len(text.strip())
    if 200 <= length <= 50000:
        score += 0.1
    return ContentQuality(
        score=max(0.0, min(1.0, score)),
        issues=issues,
        looks_blocked=looks_blocked,
    )
