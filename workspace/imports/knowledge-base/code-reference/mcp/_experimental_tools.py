"""Frozen/experimental MCP tools — kept for backward compatibility.

These tools were part of the original 40+ MCP tool surface. They have been
consolidated into the 8 core tools (see server.py) and are marked as frozen:
no new features will be added, but they remain callable for existing consumers.

To re-enable an experimental tool, move it back to server.py and promote it
from frozen to active status.
"""
from __future__ import annotations

from typing import Any

from pk_radar.core.store import KnowledgeStore
from pk_radar.ingest.web import WebIngestOptions, fetch_url_as_document


def _get_store() -> KnowledgeStore:
    """Lazy store reference — server.py sets this at init time."""
    return _store_ref


_store_ref: KnowledgeStore | None = None


def set_experimental_store(store: KnowledgeStore) -> None:
    """Called by MCPServer to inject the shared store."""
    global _store_ref
    _store_ref = store


# ---------------------------------------------------------------------------
# Legacy tool implementations
# ---------------------------------------------------------------------------

def _search_documents(args: dict[str, Any]) -> list[dict[str, Any]]:
    q = args["query"]
    limit = min(args.get("limit", 20), 100)
    rows = _get_store().search(q, limit)
    return [dict(r) for r in rows]


def _get_document(args: dict[str, Any]) -> dict[str, Any] | None:
    row = _get_store().get_document(args["doc_id"])
    return dict(row) if row else None


def _ingest_url(args: dict[str, Any]) -> dict[str, Any]:
    url = args["url"]
    tags = args.get("tags", "")
    opts = WebIngestOptions(tags=tags, mode="auto")
    doc = fetch_url_as_document(url, opts)
    doc_id = _get_store().upsert_document(doc)
    return {"id": doc_id, "title": doc.title or "Untitled", "url": url}


def _list_documents(args: dict[str, Any]) -> dict[str, Any]:
    limit = min(args.get("limit", 50), 200)
    offset = args.get("offset", 0)
    rows = _get_store().export_documents()
    total = len(rows)
    page = rows[offset : offset + limit]
    return {"items": page, "total": total, "limit": limit, "offset": offset}


def _get_stats(args: dict[str, Any]) -> dict[str, Any]:
    store = _get_store()
    sources = store.list_sources()
    tag_counts: dict[str, int] = {}
    for row in store.list_recent(10000):
        tags_raw = str(row["tags"] or "")
        if tags_raw:
            for t in tags_raw.split(","):
                t = t.strip()
                if t:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
    return {
        "documents": store.count_documents(),
        "sources": len(sources),
        "tags": len(tag_counts),
    }


def _list_tags(args: dict[str, Any]) -> list[dict[str, Any]]:
    store = _get_store()
    tag_counts: dict[str, int] = {}
    for row in store.list_recent(10000):
        tags_raw = str(row["tags"] or "")
        if tags_raw:
            for t in tags_raw.split(","):
                t = t.strip()
                if t:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
    return [{"tag": t, "count": c} for t, c in sorted(tag_counts.items())]


def _delete_document(args: dict[str, Any]) -> dict[str, Any]:
    ok = _get_store().delete_document(args["doc_id"])
    return {"ok": ok, "id": args["doc_id"]}


# ---------------------------------------------------------------------------
# Legacy tool spec definitions (frozen, not in core 8)
# ---------------------------------------------------------------------------

LEGACY_TOOL_SPECS: list[dict[str, Any]] = [
    {
        "name": "search_documents",
        "description": "[FROZEN] Search documents using FTS5 full-text search. Migrated → documents.search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 20, "maximum": 100},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_document",
        "description": "[FROZEN] Get a document by ID. Migrated → documents.get",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "integer", "description": "Document ID"},
            },
            "required": ["doc_id"],
        },
    },
    {
        "name": "ingest_url",
        "description": "[FROZEN] Ingest content from a URL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to ingest"},
                "tags": {"type": "string", "description": "Comma-separated tags"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "list_documents",
        "description": "[FROZEN] List recent documents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50, "maximum": 200},
                "offset": {"type": "integer", "default": 0},
            },
        },
    },
    {
        "name": "get_stats",
        "description": "[FROZEN] Get knowledge base statistics.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_tags",
        "description": "[FROZEN] List all tags with document counts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "delete_document",
        "description": "[FROZEN] Delete a document by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "integer", "description": "Document ID"},
            },
            "required": ["doc_id"],
        },
    },
]

LEGACY_HANDLERS: dict[str, Any] = {
    "search_documents": _search_documents,
    "get_document": _get_document,
    "ingest_url": _ingest_url,
    "list_documents": _list_documents,
    "get_stats": _get_stats,
    "list_tags": _list_tags,
    "delete_document": _delete_document,
}
