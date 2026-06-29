# API Quickstart

Run the server first:

```bash
cd backend
uv run uvicorn pk_radar.api:app --reload
```

Server starts at `http://localhost:8000`.

---

## Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{"status":"ok"}
```

---

## Create a Card

```bash
curl -X POST http://localhost:8000/cards \
  -H "Content-Type: application/json" \
  -d "{\"front\":\"What is a Rust trait?\",\"back\":\"A trait defines shared behavior that types can implement.\",\"tags\":\"rust,traits\",\"deck\":\"rust-programming\"}"
```

**Response:**
```json
{"card_id":1,"front":"What is a Rust trait?","back":"A trait defines shared behavior ...","created_at":"2026-06-23T09:15:00"}
```

---

## Review a Card (FSRS-5)

Use rating 1-4: 1=Again, 2=Hard, 3=Good, 4=Easy.

```bash
curl -X POST http://localhost:8000/cards/1/review \
  -H "Content-Type: application/json" \
  -d "{\"rating\":3}"
```

**Response:**
```json
{"card_id":1,"rating":3,"new_stability":9.2,"new_difficulty":1.9,"next_review":"2026-07-03T08:00:00","state":"review"}
```

---

## Search Documents

```bash
curl "http://localhost:8000/search?q=rust+traits&limit=5"
```

**Response:**
```json
[{"id":1,"title":"Rust Book -- Chapter 10","summary":"Overview of trait-based polymorphism","tags":"rust,programming,traits","source_type":"web","source_url":"https://example.com/rust-book/ch10","updated_at":"2026-06-22T14:30:00","rank":0.95}]
```

---

## Get Stats

```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{"total_documents":42}
```

---

## Get Due Cards

```bash
curl "http://localhost:8000/cards/due?limit=10"
```

**Response:**
```json
[{"card_id":1,"front":"What is a Rust trait?","back":"A trait defines shared behavior ...","deck":"rust-programming","stability":3.5,"difficulty":2.1,"due_at":"2026-06-23T08:00:00"}]
```

---

## List Documents

```bash
curl "http://localhost:8000/documents?limit=5"
```

---

## Get a Single Document

```bash
curl http://localhost:8000/documents/1
```

---

## Delete a Document

```bash
curl -X DELETE http://localhost:8000/documents/1
```

---

## Knowledge Graph -- Create Entity

```bash
curl -X POST http://localhost:8000/knowledge-graph/entities \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Rust\",\"entity_type\":\"topic\",\"description\":\"Systems programming language\"}"
```

---

## Knowledge Graph -- Create Relation

```bash
curl -X POST http://localhost:8000/knowledge-graph/relations \
  -H "Content-Type: application/json" \
  -d "{\"source\":\"Rust\",\"target\":\"Traits\",\"relation_type\":\"has_feature\",\"weight\":1.0}"
```

---

## MCP -- List Tools

```bash
curl http://localhost:8000/mcp/v1/tools
```

---

## MCP -- Call a Tool

```bash
curl -X POST http://localhost:8000/mcp/v1/tools/search_documents \
  -H "Content-Type: application/json" \
  -d "{\"arguments\":{\"query\":\"rust\",\"limit\":5}}"
```

---

## Next Learning Actions

```bash
curl http://localhost:8000/learning/next-actions
```

---

## Learner Profile

```bash
curl http://localhost:8000/learning/profile
```

---

## B-Line -- List Knowledge Units

```bash
curl http://localhost:8000/b-line/knowledge
```

---

## Wisdom -- Overview

```bash
curl http://localhost:8000/wisdom/overview
```

---

## AI -- List Memories

```bash
curl http://localhost:8000/ai/memories
```

---

## Pipe with jq

For readable output, pipe through `jq`:

```bash
curl -s http://localhost:8000/cards/due | jq .
curl -s http://localhost:8000/stats | jq .
curl -s "http://localhost:8000/search?q=traits" | jq .
```

---

## See Also

- [`docs/api/README.md`](README.md) -- full API reference with all endpoints
- [`docs/api/openapi.json`](openapi.json) -- machine-readable OpenAPI 3.1 spec
