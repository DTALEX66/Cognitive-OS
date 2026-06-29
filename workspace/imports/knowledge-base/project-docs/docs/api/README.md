# Knowledge Base API Reference

Local-first personal knowledge base API. All endpoints are served over HTTP at `http://localhost:8123`.

| Detail | Value |
|---|---|
| **Base URL** | `http://localhost:8123` |
| **Content-Type** | `application/json` |
| **Authentication** | None (future JWT planned) |
| **OpenAPI Spec** | [`docs/api/openapi.json`](openapi.json) |

---

## Endpoint Index

### Documents

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/documents` | List recent documents |
| `GET` | `/documents/{doc_id}` | Get a single document |
| `DELETE` | `/documents/{doc_id}` | Delete a document |
| `GET` | `/search?q={query}` | Full-text search (FTS5) |
| `GET` | `/stats` | Document count & stats |

### Cards

| Method | Path | Description |
|---|---|---|
| `GET` | `/cards` | List all cards |
| `GET` | `/cards/due` | Cards due for review |
| `POST` | `/cards` | Create a new card |
| `POST` | `/cards/{card_id}/review` | Submit an FSRS-5 review |
| `GET` | `/routes` | List learning routes |
| `GET` | `/routes/{route_id}` | Get a route |
| `POST` | `/routes` | Create a route |
| `POST` | `/routes/{route_id}/steps` | Add a step to a route |
| `GET` | `/palace` | List memory palace nodes |
| `POST` | `/palace` | Create a palace node |

### Learning

| Method | Path | Description |
|---|---|---|
| `GET` | `/learning/cognitive-load/latest` | Latest cognitive-load snapshot |
| `GET` | `/learning/cognitive-load/history` | Cognitive-load history |
| `POST` | `/learning/cognitive-load/evaluate` | Run a C-Load evaluation |
| `POST` | `/learning/encodings/suggest` | Suggest encodings for a card |
| `POST` | `/learning/encodings` | Create an encoding |
| `GET` | `/learning/skill-tasks` | List skill-building tasks |
| `POST` | `/learning/skill-tasks` | Create a skill task |
| `POST` | `/learning/skill-tasks/{task_id}/attempt` | Log a skill-task attempt |
| `POST` | `/learning/teach-back` | Start a teach-back session |
| `GET` | `/learning/teach-back/{session_id}` | Get teach-back session |
| `GET` | `/learning/consolidation/daily` | Daily consolidation digest |
| `GET` | `/learning/consolidation/weekly` | Weekly consolidation digest |
| `GET` | `/learning/next-actions` | Suggested next learning actions |
| `POST` | `/learning/diagnostics` | Run a diagnostic analysis |
| `GET` | `/learning/diagnostics/{target_type}/{target_id}` | Diagnostic history |
| `POST` | `/learning/metacognition/predict/{card_id}` | Record a prediction |
| `POST` | `/learning/metacognition/reflect/{card_id}` | Record a reflection |
| `GET` | `/learning/metacognition/report` | Calibration report |
| `GET` | `/learning/profile` | Learner profile |
| `POST` | `/learning/profile/recalculate` | Recalculate profile |
| `GET` | `/learning/profile/recommendations` | Profile-based recommendations |
| `POST` | `/learning/swarm/create` | Create a swarm team |
| `POST` | `/learning/swarm/{team_id}/add-agent` | Add an agent to a team |
| `POST` | `/learning/swarm/{team_id}/run` | Execute a swarm team |
| `GET` | `/learning/swarm/sessions` | List recent swarm sessions |
| `POST` | `/learning/b-line/dispatch` | Dispatch an agent by role |

### Review Queue

| Method | Path | Description |
|---|---|---|
| `GET` | `/review-queue` | List pending review items |
| `POST` | `/review-queue` | Submit an item for review |
| `POST` | `/review-queue/{review_id}/approve` | Approve a review |
| `POST` | `/review-queue/{review_id}/reject` | Reject a review |
| `GET` | `/review-queue/stats` | Review queue statistics |

### B-Line

| Method | Path | Description |
|---|---|---|
| `GET` | `/b-line/knowledge` | List B-Line knowledge units |
| `POST` | `/b-line/knowledge` | Create a knowledge unit |
| `GET` | `/b-line/knowledge/{unit_id}` | Get a knowledge unit |
| `GET` | `/b-line/routes` | List B-Line routes |
| `POST` | `/b-line/routes` | Create a B-Line route |
| `GET` | `/b-line/routes/{route_id}` | Get a B-Line route |
| `POST` | `/b-line/routes/{route_id}/steps` | Add step to B-Line route |
| `GET` | `/b-line/roles` | List agent roles |
| `POST` | `/b-line/context-packs` | Build a context pack |
| `GET` | `/b-line/context-packs/{pack_id}` | Get a context pack |
| `GET` | `/b-line/traces` | List trace-audit logs |
| `POST` | `/b-line/traces` | Log a trace entry |
| `GET` | `/b-line/traces/summary` | Trace failure summary |
| `GET` | `/b-line/a-to-b/candidates` | List A->B candidates |
| `POST` | `/b-line/a-to-b/translate/{card_id}` | Translate A-card to B-unit |
| `POST` | `/b-line/a-to-b/publish/{candidate_id}` | Publish an A->B candidate |
| `GET` | `/b-line/eval/runs` | List eval runs |
| `POST` | `/b-line/eval/run` | Run an evaluation |
| `GET` | `/b-line/eval/summary` | Eval summary |
| `GET` | `/b-line/feedback/anti-patterns` | List anti-patterns |
| `POST` | `/b-line/feedback/anti-patterns` | Record an anti-pattern |
| `POST` | `/b-line/feedback/b-to-a/{anti_pattern_id}` | Feedback B->A |
| `POST` | `/learning/b-line/dispatch` | Dispatch an agent by role (research/analyze/create/review/test/debug/execute) |

### Knowledge Graph

| Method | Path | Description |
|---|---|---|
| `GET` | `/knowledge-graph/entities` | Search / list entities |
| `GET` | `/knowledge-graph/entities/{name}` | Get entity and relations |
| `POST` | `/knowledge-graph/entities` | Create or update entity |
| `DELETE` | `/knowledge-graph/entities/{name}` | Delete entity |
| `POST` | `/knowledge-graph/relations` | Create a relation |
| `GET` | `/knowledge-graph/query/{entity}` | Explore graph around entity |
| `GET` | `/knowledge-graph/pinned` | List pinned entities |
| `POST` | `/knowledge-graph/pin/{name}` | Pin an entity |
| `POST` | `/knowledge-graph/unpin/{name}` | Unpin an entity |

### MCP

| Method | Path | Description |
|---|---|---|
| `GET` | `/mcp/v1/tools` | List available MCP tools |
| `POST` | `/mcp/v1/tools/{tool_name}` | Call an MCP tool |

### AI

| Method | Path | Description |
|---|---|---|
| `GET` | `/ai/memories` | List AI-generated memory entries |
| `POST` | `/ai/memories` | Create a memory entry |
| `POST` | `/ai/memories/{mem_id}/approve` | Approve a pending memory |
| `GET` | `/ai/task-packs` | List task packs |
| `POST` | `/ai/task-packs` | Create a task pack |

### Wisdom

| Method | Path | Description |
|---|---|---|
| `GET` | `/wisdom/risks` | List risk entries |
| `GET` | `/wisdom/scenarios` | List scenario entries |
| `GET` | `/wisdom/comparisons` | List comparison entries |
| `GET` | `/wisdom/competitors` | List competitor entries |
| `GET` | `/wisdom/overview` | Wisdom overview |

---

## Top 10 Endpoints -- Request and Response Examples

### 1. Health Check

```bash
GET /health
```

**Response 200:**
```json
{
  "status": "ok"
}
```

### 2. List Documents

```bash
GET /documents?limit=5&offset=0
```

**Response 200:**
```json
[
  {
    "id": 1,
    "source_type": "web",
    "source_url": "https://example.com/rust-book/ch10",
    "title": "Rust Book -- Chapter 10",
    "content": "Traits and generics in Rust ...",
    "summary": "Overview of trait-based polymorphism",
    "tags": "rust,programming,traits",
    "content_hash": "a1b2c3d4e5...",
    "created_at": "2026-06-20T10:00:00",
    "updated_at": "2026-06-22T14:30:00"
  }
]
```

### 3. Get Single Document

```bash
GET /documents/1
```

**Response 200:**
```json
{
  "id": 1,
  "source_type": "web",
  "source_url": "https://example.com/rust-book/ch10",
  "title": "Rust Book -- Chapter 10",
  "content": "Traits define shared behavior. A trait is a collection of methods ...",
  "summary": "Overview of trait-based polymorphism",
  "tags": "rust,programming,traits",
  "content_hash": "a1b2c3d4e5...",
  "created_at": "2026-06-20T10:00:00",
  "updated_at": "2026-06-22T14:30:00"
}
```

### 4. Full-Text Search

```bash
GET /search?q=rust+traits&limit=5
```

**Response 200:**
```json
[
  {
    "id": 1,
    "title": "Rust Book -- Chapter 10",
    "summary": "Overview of trait-based polymorphism",
    "tags": "rust,programming,traits",
    "source_type": "web",
    "source_url": "https://example.com/rust-book/ch10",
    "updated_at": "2026-06-22T14:30:00",
    "rank": 0.95
  }
]
```

### 5. Get Stats

```bash
GET /stats
```

**Response 200:**
```json
{
  "total_documents": 42
}
```

### 6. Create a Card

```bash
POST /cards
Content-Type: application/json

{
  "front": "What is a Rust trait?",
  "back": "A trait defines shared behavior for types to implement.",
  "tags": "rust,traits",
  "source_document_id": 1,
  "deck": "rust-programming"
}
```

**Response 200:**
```json
{
  "card_id": 1,
  "front": "What is a Rust trait?",
  "back": "A trait defines shared behavior ...",
  "created_at": "2026-06-23T09:15:00"
}
```

### 7. Get Due Cards

```bash
GET /cards/due?limit=10
```

**Response 200:**
```json
[
  {
    "card_id": 1,
    "front": "What is a Rust trait?",
    "back": "A trait defines shared behavior ...",
    "deck": "rust-programming",
    "stability": 3.5,
    "difficulty": 2.1,
    "due_at": "2026-06-23T08:00:00"
  }
]
```

### 8. Review a Card (FSRS-5)

```bash
POST /cards/1/review
Content-Type: application/json

{
  "rating": 3
}
```

**Response 200:**
```json
{
  "card_id": 1,
  "rating": 3,
  "new_stability": 9.2,
  "new_difficulty": 1.9,
  "next_review": "2026-07-03T08:00:00",
  "state": "review"
}
```

### 9. Search Knowledge Graph Entities

```bash
GET /knowledge-graph/entities?q=rust&limit=5
```

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Rust",
    "entity_type": "topic",
    "description": "Systems programming language focused on safety",
    "created_at": "2026-06-20T10:00:00",
    "updated_at": "2026-06-22T14:30:00"
  }
]
```

### 10. Next Learning Actions

```bash
GET /learning/next-actions
```

**Response 200:**
```json
{
  "actions": [
    {
      "type": "review",
      "card_id": 1,
      "reason": "Due for FSRS review",
      "priority": 0.85
    },
    {
      "type": "encoding",
      "card_id": 5,
      "reason": "Encoding suggested for weak card",
      "priority": 0.72
    },
    {
      "type": "teach-back",
      "card_id": 12,
      "reason": "Consolidation recommended",
      "priority": 0.60
    }
  ]
}
```

---

## Authentication

Authentication is available for multi-user scenarios:

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login, returns JWT access + refresh tokens |
| `POST` | `/auth/refresh` | Refresh an expired access token |
| `POST` | `/auth/api-keys` | Create an API key |
| `GET` | `/auth/api-keys` | List API keys with stats |
| `DELETE` | `/auth/api-keys/{key_id}` | Revoke an API key |

Use `Authorization: Bearer <token>` for protected endpoints.

---

## FSRS-5 Review Ratings

The `/cards/{card_id}/review` endpoint uses the **FSRS-5** spaced-repetition algorithm. Accepted rating values:

| Rating | Meaning |
|---|---|
| `1` | Again -- complete failure to recall |
| `2` | Hard -- recalled with significant difficulty |
| `3` | Good -- recalled with acceptable effort |
| `4` | Easy -- recalled effortlessly |

After each review the card stability, difficulty, and next-review date are recalculated.

---

## MCP Tool Integration

The API includes a built-in MCP (Model Context Protocol) server at `/mcp/v1/`. Available tools:

| Tool | Description |
|---|---|---|
| `health.check` | System health (uptime, DB status, version) |
| `documents.search` | FTS5 full-text search |
| `documents.get` | Retrieve a document by ID |
| `cards.create` | Create a spaced-repetition card |
| `cards.due` | List review cards due now |
| `reviews.submit` | Submit a review (again/hard/good/easy) |
| `context_pack.build` | Build context pack for downstream agents |
| `taskpack.generate` | Generate structured task list |
| `search_documents` | [Frozen] Legacy search |
| `get_document` | [Frozen] Legacy document get |
| `ingest_url` | [Frozen] URL ingestion |
| `list_documents` | [Frozen] List documents |
| `get_stats` | [Frozen] KB statistics |
| `list_tags` | [Frozen] List all tags |
| `delete_document` | [Frozen] Delete document |

---

## OpenAPI Spec

The full machine-readable spec is available at [`docs/api/openapi.json`](openapi.json). It can be imported into Swagger UI, Postman, or any OpenAPI-compatible tool.

---

## See Also

- [`docs/api/QUICKSTART.md`](QUICKSTART.md) -- curl recipes for common operations
- [`backend/pk_radar/api.py`](../../backend/pk_radar/api.py) -- route definitions
- [`backend/pk_radar/schemas.py`](../../backend/pk_radar/schemas.py) -- Pydantic models
