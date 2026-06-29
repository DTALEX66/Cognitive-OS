from __future__ import annotations

import re

CJK_RE = re.compile(r'[\u4e00-\u9fff]+')
LATIN_RE = re.compile(r'[a-z0-9][a-z0-9_-]*')


def lexical_terms(text: str) -> set[str]:
    normalized = text.lower()
    terms = set(LATIN_RE.findall(normalized))

    for segment in CJK_RE.findall(normalized):
        terms.add(segment)
        if len(segment) > 1:
            terms.update(segment[index:index + 2] for index in range(len(segment) - 1))

    return {term for term in terms if term.strip()}
