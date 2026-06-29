# Agent Schema Reference

Each agent markdown file follows this structure.

## Frontmatter (YAML)

Required fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Human-readable agent name |
| `slug` | string | File name and TOML identifier |
| `description` | string | One-line purpose |
| `team` | enum | `foundation`, `research`, `engineering`, `ops`, `testing` |
| `priority` | enum | `p0` (core), `p1` (important), `p2` (nice-to-have) |
| `tools` | list | Allowed tool types |
| `outputs` | list | Required deliverables |
| `risk_level` | enum | `low`, `medium`, `high` |

## Body Sections

Every agent must include these sections:

- **Identity** — Role statement
- **Mission** — One-paragraph purpose
- **Responsibilities** — Behavioral constraints
- **Inputs** — What the agent receives
- **Outputs** — What the agent produces
- **Hard Rules** — Non-negotiable constraints
- **Workflow** — Step-by-step process
- **Quality Gates** — Pass/fail checks
- **Failure Modes** — Known failure patterns
- **Escalation** — When to escalate
- **Success Metrics** — How completion is measured

## Hierarchy

```
MASTER_SPEC
> API_CONTRACT
> DATA_SCHEMA
> AGENT_ROLE
> TASK_PROMPT
> MODEL_OUTPUT
```

Agent roles cannot override project-level specifications.
