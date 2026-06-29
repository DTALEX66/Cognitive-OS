# Knowledge-Base Agent Role System

This directory documents the **Agent Role System** — a lightweight set of agent role definitions
tailored for Knowledge-Base development, research, operations, and testing.

## Origin

This system was inspired by [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) (MIT License).
We absorbed the **structural template design**, **multi-tool conversion pattern**, and **Codex TOML output format**,
but did **not** replicate the full 232-agent catalog. Instead, we selected 16 core roles that directly serve
Knowledge-Base P0 development, DEEP parallel engineering, and CODEX operations.

See [agent_schema.md](agent_schema.md) for the schema reference and
[agency_agents_reference.md](agency_agents_reference.md) for the upstream attribution.

## Directory Layout

```
agents/
├── foundation/       — Orchestration, parallel dispatch, task packs, evidence
├── research/         — GitHub analysis, onboarding, license audit, synthesis
├── engineering/      — Backend API, frontend UI, file ingest, search
├── ops/              — CODEX ops, DevOps, security, release management
└── testing/          — API testing, regression, prompt injection, benchmarks
```

## Quick Start

```bash
# Validate all agents
python scripts/validate-agents.py

# Convert to Codex TOML
python scripts/convert-agents.py --tool codex

# Install to Codex (dry run)
powershell ./scripts/install-agents.ps1 -Tool codex -DryRun
bash ./scripts/install-agents.sh --tool codex --dry-run
```

## License

The Agent Role System is part of Knowledge-Base.
Third-party inspiration from agency-agents is used under MIT License — see [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
