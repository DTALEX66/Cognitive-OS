# MCP Tools — 8 Core Interface

The `pk_radar` MCP server exposes 8 core tools plus a set of frozen legacy tools for backward compatibility.

## 8 Core Tools

| # | Tool | Description |
|---|------|-------------|
| 1 | `health.check` | System health — uptime, DB status, version info |
| 2 | `documents.search` | Full-text search via FTS5 |
| 3 | `documents.get` | Retrieve a single document by ID |
| 4 | `cards.create` | Create a spaced-repetition / review card |
| 5 | `cards.due` | List review cards due now |
| 6 | `reviews.submit` | Submit a review result (again/hard/good/easy) |
| 7 | `context_pack.build` | Assemble document snapshot + stats for downstream agents |
| 8 | `taskpack.generate` | Generate a structured task list from a topic |

## Frozen / Experimental Tools

The original ~40 legacy tools have been consolidated into 7 frozen tools kept only for backward compatibility. They are defined in `_experimental_tools.py` and are **not** part of the active core:

- `search_documents` → migrated to `documents.search`
- `get_document` → migrated to `documents.get`
- `ingest_url`
- `list_documents`
- `get_stats`
- `list_tags`
- `delete_document`

These tools will not receive new features. New consumers should use the 8 core tools above.

## Files

| File | Role |
|------|------|
| `server.py` | MCPServer + FastAPI transport — registers 8 core + legacy tools |
| `_experimental_tools.py` | Frozen legacy tool implementations and specs |
| `tool_schema.py` | `MCPToolSpec` / `MCPTool` dataclasses |
| `tool_registry.py` | Generic tool registry with alias support |
| `audit.py` | Audit log for tool calls |
| `permissions.py` | Access-level permission checks |
| `__init__.py` | Public exports (`MCPServer`, `attach_mcp_routes`) |

## API Endpoints

```
GET  /mcp/v1/tools           → list all registered tools
POST /mcp/v1/tools/{name}    → call a tool by name
```

## Testing

```powershell
$env:PYTHONPATH="backend"
python -m pytest backend/tests/test_mcp.py backend/tests/test_mcp_tool_registry.py -v
```
