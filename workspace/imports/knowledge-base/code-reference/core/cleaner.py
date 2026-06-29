from __future__ import annotations
from typing import Any

class DataCleaner:
    def __init__(self, store: Any) -> None:
        self._store = store

    def remove_empty_documents(self) -> int:
        cur = self._store.conn.execute(
            "DELETE FROM documents WHERE content IS NULL OR content = ''"
        )
        self._store.conn.commit()
        return cur.rowcount

    def deduplicate_by_hash(self) -> int:
        cur = self._store.conn.execute(
            "DELETE FROM documents WHERE id NOT IN (SELECT MIN(id) FROM documents WHERE content_hash != '' GROUP BY content_hash) AND content_hash != ''"
        )
        self._store.conn.commit()
        return cur.rowcount

    def fix_null_titles(self) -> int:
        cur = self._store.conn.execute(
            "UPDATE documents SET title='' WHERE title IS NULL"
        )
        self._store.conn.commit()
        return cur.rowcount

    def vacuum(self) -> None:
        self._store.conn.execute("PRAGMA optimize")
        self._store.conn.execute("VACUUM")
        self._store.conn.commit()

# === Backward compatibility ===

def html_to_markdown(html: str) -> str:
    '''Convert HTML to plain text. Old test compatibility.'''
    from pk_radar.core.xss_protection import strip_html_tags
    return strip_html_tags(html)

def simple_title_from_markdown(md: str, fallback: str = "Untitled") -> str:
    '''Extract first heading line from markdown.'''
    for line in md.splitlines():
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        if line.startswith('## '):
            return line[3:].strip()
    return md if md else fallback[:80].strip()
