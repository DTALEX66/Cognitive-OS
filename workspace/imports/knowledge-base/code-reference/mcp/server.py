from __future__ import annotations

import json
from typing import Any

from pk_radar.config import get_settings
from pk_radar.core.store import KnowledgeStore
from pk_radar.ingest.web import WebIngestOptions, fetch_url_as_document
from pk_radar.ingest.files import ingest_text_file

# ── experimental / frozen tools ───────────────────────────────────────────
from pk_radar.mcp._experimental_tools import (
    LEGACY_TOOL_SPECS,
    LEGACY_HANDLERS,
    set_experimental_store,
)

settings = get_settings()
store = KnowledgeStore(settings.db_path)
store.init()

# Share store with experimental tools module
set_experimental_store(store)


# ── 8 Core tool specs ─────────────────────────────────────────────────────

CORE_TOOL_SPECS: list[dict[str, Any]] = [
    # 1 ─ health.check
    {
        "name": "health.check",
        "description": "Check system health — returns uptime, DB status, and version info.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    # 2 ─ documents.search
    {
        "name": "documents.search",
        "description": "Search documents using FTS5 full-text search.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 20, "maximum": 100},
            },
            "required": ["query"],
        },
    },
    # 3 ─ documents.get
    {
        "name": "documents.get",
        "description": "Get a document by ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "doc_id": {"type": "integer", "description": "Document ID"},
            },
            "required": ["doc_id"],
        },
    },
    # 4 ─ cards.create
    {
        "name": "cards.create",
        "description": "Create a spaced-repetition or review card.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "front": {"type": "string", "description": "Card front / question"},
                "back": {"type": "string", "description": "Card back / answer"},
                "tags": {"type": "string", "description": "Comma-separated tags"},
            },
            "required": ["front", "back"],
        },
    },
    # 5 ─ cards.due
    {
        "name": "cards.due",
        "description": "List review cards that are due now.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20, "maximum": 100},
            },
        },
    },
    # 6 ─ reviews.submit
    {
        "name": "reviews.submit",
        "description": "Submit a review result for a card (pass / fail / easy / hard).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "card_id": {"type": "integer", "description": "Card ID"},
                "rating": {
                    "type": "string",
                    "description": "Review rating: again, hard, good, easy",
                    "enum": ["again", "hard", "good", "easy"],
                },
            },
            "required": ["card_id", "rating"],
        },
    },
    # 7 ─ context_pack.build
    {
        "name": "context_pack.build",
        "description": "Build a context pack: assemble recent documents, cards, and stats into a single payload for downstream agents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "include_cards": {"type": "boolean", "default": True},
                "max_docs": {"type": "integer", "default": 10, "maximum": 50},
            },
        },
    },
    # 8 ─ taskpack.generate
    {
        "name": "taskpack.generate",
        "description": "Generate a task pack: create a structured task list from knowledge base insights.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Topic to generate tasks for"},
                "count": {"type": "integer", "default": 5, "maximum": 20},
            },
        },
    },
]


# ── Core tool handlers ────────────────────────────────────────────────────

def _health_check(args: dict[str, Any]) -> dict[str, Any]:
    """Health-check: basic liveness + DB status."""
    import sys, platform, time
    try:
        store.count_documents()
        db_ok = True
    except Exception:
        db_ok = False
    return {
        "status": "ok" if db_ok else "degraded",
        "db": "ok" if db_ok else "unavailable",
        "python": sys.version,
        "platform": platform.platform(),
        "timestamp": time.time(),
    }


def _documents_search(args: dict[str, Any]) -> list[dict[str, Any]]:
    q = args["query"]
    limit = min(args.get("limit", 20), 100)
    rows = store.search(q, limit)
    return [dict(r) for r in rows]


def _documents_get(args: dict[str, Any]) -> dict[str, Any] | None:
    row = store.get_document(args["doc_id"])
    return dict(row) if row else None


def _cards_create(args: dict[str, Any]) -> dict[str, Any]:
    """Stub — card storage not implemented yet; returns accepted payload."""
    return {
        "id": None,
        "status": "accepted",
        "front": args["front"],
        "back": args["back"],
        "tags": args.get("tags", ""),
    }


def _cards_due(args: dict[str, Any]) -> dict[str, Any]:
    """Stub — always returns empty list until card engine is wired."""
    return {"cards": [], "due_count": 0}


def _reviews_submit(args: dict[str, Any]) -> dict[str, Any]:
    """Stub — always accepts review; real scheduling TBD."""
    return {
        "card_id": args["card_id"],
        "rating": args["rating"],
        "status": "recorded",
        "next_due": None,
    }


def _context_pack_build(args: dict[str, Any]) -> dict[str, Any]:
    """Stub — assembles basic document snapshot + card count."""
    max_docs = min(args.get("max_docs", 10), 50)
    rows = store.export_documents()
    docs = rows[:max_docs]
    return {
        "documents": docs,
        "document_count": len(docs),
        "cards_due": 0,
        "stats": _health_check({}),
    }


def _taskpack_generate(args: dict[str, Any]) -> dict[str, Any]:
    """Stub — returns a simple task list based on topic."""
    topic = args.get("topic", "general")
    count = min(args.get("count", 5), 20)
    return {
        "topic": topic,
        "tasks": [
            {"id": i + 1, "title": f"Review {topic} — item {i + 1}", "status": "pending"}
            for i in range(count)
        ],
    }


CORE_HANDLERS: dict[str, Any] = {
    "health.check": _health_check,
    "documents.search": _documents_search,
    "documents.get": _documents_get,
    "cards.create": _cards_create,
    "cards.due": _cards_due,
    "reviews.submit": _reviews_submit,
    "context_pack.build": _context_pack_build,
    "taskpack.generate": _taskpack_generate,
}


# ── MCPServer ─────────────────────────────────────────────────────────────


class MCPServer:
    name = "knowledge-base-mcp"

    def list_tools(self) -> list[dict[str, Any]]:
        """Return 8 core tools + frozen legacy tools for backward compat."""
        return CORE_TOOL_SPECS + LEGACY_TOOL_SPECS

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        # Try core handlers first, then legacy
        handler = CORE_HANDLERS.get(name) or LEGACY_HANDLERS.get(name)
        if not handler:
            return {"error": f"Unknown tool: {name}"}
        try:
            result = handler(arguments)
            return {"result": result}
        except Exception as exc:
            return {"error": str(exc)}


# ── FastAPI-based MCP transport ───────────────────────────────────────────

from fastapi import APIRouter, FastAPI

mcp_server = MCPServer()
router = APIRouter(prefix="/mcp/v1")


@router.get("/tools")
def list_tools():
    return {"tools": mcp_server.list_tools()}


@router.post("/tools/{tool_name}")
def call_tool(tool_name: str, body: dict[str, Any]):
    return mcp_server.call_tool(tool_name, body.get("arguments", {}))


def attach_mcp_routes(app: FastAPI) -> FastAPI:
    app.include_router(router)
    return app
