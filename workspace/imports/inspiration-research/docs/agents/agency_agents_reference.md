# agency-agents Reference

This document acknowledges [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)
as the upstream inspiration for Knowledge-Base Agent Role System.

## What We Absorbed

| Pattern | Our Implementation |
|---------|-------------------|
| Agent markdown structure | Schema with frontmatter + body sections |
| Multi-tool conversion | `scripts/convert-agents.py` (Python, rewritten from convert.sh) |
| Install scripts | `scripts/install-agents.ps1` + `install-agents.sh` (dual-platform) |
| Codex TOML output | `integrations/codex/agents/*.toml` |
| NEXUS orchestration concept | Adapted into KB Orchestrator + DEEP Parallel Conductor workflow |
| Dev->QA loop | Built into agent workflows with Evidence Collector handoff |
| Evidence-first output | Success Metrics and Quality Gates in every agent |

## What We Did Not Copy

- We did **not** replicate all 232 agents.
- We did **not** import any AGPL/GPL code.
- We selected **16 roles** that directly serve Knowledge-Base P0 development, DEEP engineering, and CODEX operations.

## License

`agency-agents` is MIT Licensed. This reference is provided in compliance with the license terms.
