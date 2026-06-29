# 008 External Project Integration Plan

> Target phase: Phase 1 -> Phase 3 capability promotion
> Scope: integrate reusable assets from `D:\Project Directory` into Cognitive-OS through small, tested promotions.
> Rule: no bulk copy, no secrets, no runtime databases, no `.git`, no virtualenvs, no node_modules.

## 1. Goal

把 `D:\Project Directory` 里的可用项目逐步并入当前 `Cognitive-OS`，但保持本仓库的边界清晰：

```text
Cognitive-OS = front runtime + routing + memory + execution trace + learning loop
KnowledgeBase = strongest implementation source
Inspiration Research = architecture/source-of-truth design source
Obsidian skills = upstream note/vault ingestion reference
Screen-Translation-Assistant = future OCR/sidecar reference
Codex/OpenHarness/Ponytail/Claw = agent/tool/sandbox design reference
```

并入方式必须是：

```text
Source module
  -> Contract mapping
  -> Minimal target module
  -> Tests
  -> Intake note
  -> Optional API exposure
```

## 2. Source Inventory

| Source | Local path | Integration value | Use mode |
| --- | --- | --- | --- |
| KnowledgeBase | `D:\Project Directory\KnowledgeBase` | Highest value: working backend, FSRS, search, B-line agent/runtime modules, A-line learning modules | Adapt into runtime code |
| Inspiration Research | `D:\Project Directory\Inspiration Research` | Architecture, A/B maps, subsystem design docs | Keep as design source; promote through intake |
| obsidian-skills | `D:\Project Directory\Obsidian-Ecosystem\obsidian-skills` | Obsidian markdown, bases, canvas, CLI, defuddle skill patterns | Adapt into ingestion/profile design |
| Screen-Translation-Assistant | `D:\Project Directory\Screen-Translation-Assistant` | OCR sidecar, screenshot/hotkey/desktop patterns, local glossary/cache | Future sidecar and OCR ingestion reference |
| AI-Agent-Tools/codex | `D:\Project Directory\AI-Agent-Tools\codex` | Codex architecture: sandbox, plugin, thread, tool, model provider, skills | Reference only |
| AI-Agent-Tools/OpenHarness | `D:\Project Directory\AI-Agent-Tools\OpenHarness` | Python CLI agent architecture, MCP, Textual/Typer CLI | Reference only until agent runtime grows |
| AI-Agent-Tools/ponytail | `D:\Project Directory\AI-Agent-Tools\ponytail` | Skills/hooks/plugin package patterns | Reference for skill packaging |
| claw-code | `D:\Project Directory\claw-code` | Rust agent harness, sandbox, CLI parity ideas | Reference only |
| ClaudeCode artifacts | `D:\Project Directory\ClaudeCode` | Extracted source/package artifacts | Research only; do not copy code into runtime |
| Unlimited-OCR | `D:\Project Directory\OCR\Unlimited-OCR` | PDF + wheel artifact, not a clear source project | Optional OCR experiment only |

## 3. Target Runtime Shape

Current target modules should stay small and explicit:

```text
app/
  core/
    router.py          # attention route
    text.py            # lexical tokenization/scoring helpers
    policy.py          # safety and source validation
  ingestion/
    file.py            # local file ingestion
    web.py             # future web ingestion
    obsidian.py        # future Obsidian/vault ingestion
    ocr.py             # future OCR/image text ingestion
    quality.py         # content quality and cleaning
  rag/
    retriever.py       # context retrieval entrypoint
    context_engine.py  # promoted ContextPack scoring/ranking
  memory/
    store.py           # current jsonl store
    sqlite_store.py    # future durable local store
  learning/
    fsrs.py            # future FSRS scheduling
    cards.py           # future review/card models
    teach_back.py      # future teach-back loop
    rubrics.py         # future assessment rubrics
  evaluation/
    evaluator.py       # trace evaluation entrypoint
    trace_audit.py     # future trace analyzer
    lesson_engine.py   # future lesson extraction/prioritization
  tools/
    registry.py        # tool metadata and handlers
    guard.py           # future risk gate
    sandbox.py         # future local sandbox wrapper
  agent/
    planner.py
    executor.py
    orchestrator.py    # future graph/role orchestration
```

## 4. Promotion Phases

### Phase 0 - Baseline Hygiene

Status: started.

Goals:

- Keep the current FastAPI runtime runnable.
- Add tests around routing and lexical retrieval.
- Keep generated `data/`, `.venv`, caches, and local state ignored.
- Do not resolve unrelated line-ending changes in imported reference files unless explicitly needed.

Acceptance:

- `python -m unittest discover -s tests` passes.
- `python -m compileall app tests` passes.
- `/run` handles Chinese TASK input and writes trace/lesson.

### Phase 1 - Runtime Spine Stabilization

Source priority:

- Current Cognitive-OS app
- KnowledgeBase `pk_radar/b_line/context_engine.py`
- KnowledgeBase `pk_radar/core/quality.py`
- KnowledgeBase `pk_radar/core/cleaner.py`

Target work:

1. Add API-level smoke tests with FastAPI `TestClient`.
2. Promote deterministic ContextPack ranking into `app/rag/context_engine.py`.
3. Add content quality signals in `app/ingestion/quality.py`.
4. Keep memory backend as JSONL until contracts settle.

Acceptance:

- `/health`, `/route`, `/run`, `/memory/search`, `/tools` are covered by tests.
- Context scoring explains `item_count`, term overlap, source quality, recency when available.
- Chinese and English inputs both retrieve matching memory.
- No new external services required.

### Phase 2 - B-Line Machine Runtime

Source priority:

- `pk_radar/b_line/trace_audit.py`
- `pk_radar/b_line/machine_lesson.py`
- `pk_radar/b_line/feedback_loop.py`
- `pk_radar/b_line/mcp_guard.py`
- `pk_radar/b_line/sandbox_executor.py`
- `pk_radar/b_line/model_router.py`

Target work:

1. Replace generic `compile_lesson()` with a deterministic `LessonEngine`.
2. Add `TraceAudit` that scores execution traces for failure class, missing evidence, blocked tools, and repeat patterns.
3. Expand tool registry with a guard layer:
   - dry-run default for medium/high risk
   - explicit review requirement for high risk
   - path containment checks
   - audit events
4. Keep model router as metadata only until real model providers are configured.

Acceptance:

- `/run` returns richer `eval` and `lesson` fields.
- A blocked tool creates a failure lesson with evidence trace id.
- High-risk tool names cannot execute without REVIEW.
- Tests cover success trace, blocked trace, and high-risk trace.

### Phase 3 - A-Line Human Learning Loop

Source priority:

- `pk_radar/core/fsrs5.py`
- `pk_radar/core/fsrs_optimizer_adapter.py`
- `knowledge_base/encoding.py`
- `knowledge_base/teach_back.py`
- `knowledge_base/rubrics.py`
- `knowledge_base/cognitive_load.py`

Target work:

1. Add `app/learning/` package.
2. Introduce `LearningCard`, `ReviewEvent`, `FSRSState`, and `ReviewSchedule` schemas.
3. Add local card generation from KB-routed documents.
4. Add review endpoint candidates:
   - `POST /learning/cards`
   - `POST /learning/review`
   - `GET /learning/due`
5. Keep optimizer later; first port deterministic FSRS scheduling only.

Acceptance:

- KB-routed material can become review cards.
- Review grade updates stability/difficulty/due time.
- No old KnowledgeBase database schema is required.
- Tests cover new card, review update, due filter.

### Phase 4 - Ingestion Expansion

Source priority:

- KnowledgeBase `pk_radar/adapters/converters/native_text.py`
- KnowledgeBase `pk_radar/adapters/crawlers/httpx_adapter.py`
- KnowledgeBase `pk_radar/core/policy.py`
- obsidian-skills `skills/obsidian-markdown/SKILL.md`
- obsidian-skills `skills/json-canvas/SKILL.md`
- Screen-Translation-Assistant `sidecars/ocr_service/main.py`

Target work:

1. Add `app/ingestion/obsidian.py` for vault-local markdown semantics:
   - wikilinks
   - frontmatter/properties
   - tags
   - embeds as references, not raw binary import
2. Add conservative web ingestion:
   - allowlist/denylist policy
   - no stealth scraping by default
   - source metadata
3. Add OCR ingestion as future optional sidecar:
   - start with API contract and mock mode
   - keep heavy engines optional
   - do not vendor `.venv` or model files

Acceptance:

- Directory ingestion can label source profile: `obsidian`, `knowledge-base`, `inspiration-research`.
- Obsidian wikilinks become metadata edges.
- Web ingestion refuses unsafe/private URLs.
- OCR endpoint can accept a local image path in mock mode before real engine integration.

### Phase 5 - Durable Storage And Search

Source priority:

- KnowledgeBase `pk_radar/core/store.py`
- KnowledgeBase migrations under `pk_radar/core/migrations/`
- KnowledgeBase vector adapter patterns

Target work:

1. Keep JSONL as fallback.
2. Add SQLite backend behind a store interface.
3. Add FTS lexical search before vector DB.
4. Add migration runner only after schemas are stable.

Acceptance:

- `memory.backend` can switch between `jsonl` and `sqlite`.
- Existing JSONL tests still pass.
- SQLite tests run against temp files only.
- No imported runtime databases are committed.

### Phase 6 - Frontend/API Surface

Source priority:

- KnowledgeBase frontend pages only as UX reference.
- Do not directly migrate the full Next.js app into Phase 1 runtime.

Target work:

1. Finish backend API contracts first.
2. Add OpenAPI-oriented docs and examples.
3. Later decide between:
   - lightweight local dashboard inside Cognitive-OS
   - separate frontend package
   - reuse selected KnowledgeBase UI patterns

Acceptance:

- Backend API remains usable without frontend.
- Frontend work does not introduce broad dependency churn.

### Phase 7 - Agent Orchestration

Source priority:

- Codex `codex-rs` architecture as design reference
- OpenHarness CLI patterns
- KnowledgeBase `pk_radar/b_line/agent_orchestrator.py`
- Ponytail skills/hooks package patterns
- Claw Code sandbox/CLI notes as reference only

Target work:

1. Add graph-style `TaskPack` planning only after tools and trace are stable.
2. Add role metadata for planner/executor/reviewer.
3. Keep all external tool execution dry-run or explicitly confirmed.
4. Model provider config remains stub until private credentials are configured locally.

Acceptance:

- Multi-step task graph can run with local echo/file tools.
- Trace records role, step, tool, risk, result.
- No credential or connector state is stored in repo.

## 5. Source-To-Target Map

| Priority | Source file or folder | Target | Reason |
| ---: | --- | --- | --- |
| 1 | `KnowledgeBase/.../pk_radar/b_line/context_engine.py` | `app/rag/context_engine.py` | Directly improves `/run` context quality |
| 2 | `KnowledgeBase/.../pk_radar/core/quality.py` | `app/ingestion/quality.py` | Better DROP/REVIEW/KB routing evidence |
| 3 | `KnowledgeBase/.../pk_radar/b_line/trace_audit.py` | `app/evaluation/trace_audit.py` | Makes trace evaluation explainable |
| 4 | `KnowledgeBase/.../pk_radar/b_line/machine_lesson.py` | `app/evaluation/lesson_engine.py` | Replaces generic machine lessons |
| 5 | `KnowledgeBase/.../pk_radar/b_line/mcp_guard.py` | `app/tools/guard.py` | Strengthens tool safety gates |
| 6 | `KnowledgeBase/.../pk_radar/core/fsrs5.py` | `app/learning/fsrs.py` | Adds human learning review loop |
| 7 | `KnowledgeBase/.../knowledge_base/teach_back.py` | `app/learning/teach_back.py` | Adds teach-back workflow |
| 8 | `obsidian-skills/skills/obsidian-markdown` | `app/ingestion/obsidian.py` + fixtures | Supports Obsidian as upstream input |
| 9 | `Screen-Translation-Assistant/sidecars/ocr_service/main.py` | `app/ingestion/ocr.py` or `sidecars/ocr_service` | Future image/OCR ingestion |
| 10 | `AI-Agent-Tools/codex/codex-rs/*` | docs/reference only | Architecture ideas, not runtime copy |

## 6. Non-Negotiable Boundaries

Do not import:

- `.env`
- `.git`
- `node_modules`
- `.venv`
- `__pycache__`
- SQLite/database files
- logs
- model weights
- connector credentials
- personal vault absolute paths
- browser cookies
- local Codex state

Do not do:

- replace Cognitive-OS with KnowledgeBase wholesale
- add full frontend before backend contracts stabilize
- introduce real web scraping or OCR engines as required dependencies in Phase 1
- copy ClaudeCode artifact code into runtime
- commit generated memory/traces from smoke tests

## 7. First Three Implementation Rounds

### Round 1 - Test And Context Spine

Files:

- `tests/test_api_smoke.py`
- `app/rag/context_engine.py`
- `app/rag/retriever.py`
- `app/ingestion/quality.py`

Acceptance:

- API smoke tests pass.
- ContextPack scoring has stable reasons.
- Chinese retrieval tests remain green.

### Round 2 - Trace Audit And Lesson Engine

Files:

- `app/evaluation/trace_audit.py`
- `app/evaluation/lesson_engine.py`
- `app/evaluation/feedback.py`
- `tests/test_trace_lesson.py`

Acceptance:

- Successful trace creates success lesson with evidence.
- Blocked/error trace creates failure lesson with actionable future constraint.
- `/run` still returns previous fields plus richer evaluation detail.

### Round 3 - Tool Guard

Files:

- `app/tools/guard.py`
- `app/tools/registry.py`
- `tests/test_tool_guard.py`

Acceptance:

- Medium risk write remains dry-run by default.
- High risk execution remains blocked.
- Path traversal is blocked.
- Tool results include guard reasons.

## 8. Rollback Plan

Each round must be reversible by removing its target files and restoring touched entrypoints.

Preferred rollback unit:

```powershell
git restore -- app/<touched-module> tests/<touched-test>
```

Only use explicit paths. Do not use `git reset --hard` unless separately confirmed.

## 9. Done Criteria

The integration is considered healthy when:

- `python -m unittest discover -s tests` passes.
- `python -m compileall app tests` passes.
- `/run` still completes for a Chinese TASK input.
- `/route` still sends high-risk input to REVIEW.
- No private or generated files appear in `git status --short`.
- Every promoted source has a source-to-target note in an intake card.
