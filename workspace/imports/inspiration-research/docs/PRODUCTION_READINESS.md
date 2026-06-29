# Production Readiness Checklist

> Knowledge-Base v0.1.4 — Local-first personal knowledge base

## Security

- [ ] All API endpoints behind nginx reverse proxy
- [ ] Security headers configured (X-Content-Type-Options, X-Frame-Options, XSS-Protection, Referrer-Policy)
- [ ] CORS restricted to allowed origins in production
- [ ] .env file excluded from Docker image (.dockerignore)
- [ ] No secrets in docker-compose files (use .env or Docker secrets)
- [ ] SQLite WAL mode enabled (journal_mode=WAL)
- [ ] Client max body size limited (50M in nginx)
- [ ] MCP endpoints authenticated (audit logging enabled)
- [ ] URL allowlist enforced via SecurityPolicy
- [ ] ReviewGate enabled for AI-generated content
- [ ] FSRS-5 spaced repetition without external data leak
- [ ] Gitleaks, Trivy, Semgrep, OSV-Scanner in CI pipeline
- [ ] Python security scan in CI pipeline

## Performance

- [ ] nginx gzip compression enabled (recommended)
- [ ] SQLite indexes created on all query-critical columns (15 indexes)
- [ ] FTS5 virtual tables for full-text search
- [ ] Pagination on all list endpoints (limit/offset)
- [ ] Resource limits set in docker-compose.prod.yml
  - Backend: 512M memory, 1.0 CPU
  - Frontend: 512M memory, 0.5 CPU
  - Nginx: 128M memory, 0.25 CPU
- [ ] Docker healthchecks configured with appropriate intervals
- [ ] Log rotation enabled (json-file, 10MB max, 3 files)
- [ ] Frontend static assets served by nginx (recommended)
- [ ] Database vacuum/analyze on schedule

## Reliability

- [ ] Restart policy: always (production), unless-stopped (dev)
- [ ] Database backups configured (scripts/deploy.ps1 includes backup)
- [ ] WAL checkpoint on clean shutdown
- [ ] Health check endpoints: /health (backend), / (frontend)
- [ ] Graceful shutdown handling in FastAPI lifespan
- [ ] Data persisted in named Docker volume (kb_data)
- [ ] All database tables use CREATE TABLE IF NOT EXISTS (idempotent migrations)
- [ ] MigrationRunner supports versioned SQL migrations

## Monitoring

- [ ] Docker container health checks active
- [ ] Log aggregation via json-file driver
- [ ] Application events logged to events table
- [ ] Execution traces logged to execution_traces table
- [ ] Agent task history tracked in agent_task_history
- [ ] Cognitive load metrics recorded in cognitive_load_events
- [ ] API request logging (recommended: add middleware)
- [ ] Error rate monitoring via eval_runs + anti_patterns

## API Coverage

- [ ] /health — health check
- [ ] /api/ — all backend routes proxied to backend:8000
- [ ] /docs — OpenAPI documentation
- [ ] /openapi.json — OpenAPI spec
- [ ] /mcp/ — MCP tool server endpoints (120s timeout)
- [ ] /api/v2/ — future API versioning

## Database Schema (47 tables verified)

| Category | Tables |
|----------|--------|
| Core | documents, sources, entities, relations, observations, sessions, events |
| A-Line (Human) | cards, reviews, learning_routes, route_steps, palace_nodes |
| A-Line (Learning) | cognitive_load_events, memory_encodings, encoding_strategies, skill_tasks, skill_attempts, rubric_templates, teach_back_sessions, diagnostics, metacognition_events, learner_profile, mastery_assessments |
| B-Line (Machine) | machine_knowledge_units, machine_routes, route_steps_b, a_to_b_candidates |
| B-Line (Agent) | agent_roles, agent_task_history, execution_traces |
| AI System | ai_candidate_memories, task_packs |
| Review | review_queue |
| Evaluation | eval_runs, anti_patterns |
| Context | context_packs |

## CI/CD Pipeline

- [ ] backend-core: store, ingest, search tests
- [ ] backend-a-line: FSRS-5, cognitive_load, encoding, skills, rubrics, teach_back, evolution, quality, policy
- [ ] backend-b-line: machine_knowledge, agent, A-to-B, benchmark, B-line, smart_router
- [ ] backend-integration: API, MCP, security, isolation, adapters, CLI, exporter, scanner, converters
- [ ] frontend: npm ci + npm run build
- [ ] Security: gitleaks, trivy, semgrep, osv-scanner, python-security
- [ ] Preflight checks on PR

## Pre-Deployment Verification

- [ ] `docker compose build` succeeds
- [ ] `docker compose up -d` starts all services
- [ ] `curl http://localhost:80/health` returns OK
- [ ] All 47 database tables created on first init
- [ ] E2E test script passes (scripts/e2e-test.ps1)
- [ ] Frontend loads at http://localhost
- [ ] Backend unit tests pass locally

## Rollback Plan

1. Stop containers: `docker compose down`
2. Restore database from backup
3. Rebuild previous version: `git checkout <previous-tag>`
4. Restart: `docker compose up -d`
