# Local Imports

> Created: 2026-06-29
> Location: `workspace/local-imports/D-Project-Directory-2026-06-29/`
> Status: local-only snapshot, ignored by Git.

This folder preserves useful materials from `D:\Project Directory` before that source area is cleaned up. It is intentionally ignored by Git because it contains full external source snapshots and third-party/reference artifacts.

## Copied Snapshots

| Snapshot | Source | Files | Size | Use |
| --- | --- | ---:| ---:| --- |
| `knowledge-base` | `D:\Project Directory\KnowledgeBase` | 717 | 13.2 MB | Primary implementation source for FSRS, memory/search, B-line runtime, A-line learning |
| `inspiration-research` | `D:\Project Directory\Inspiration Research` | 32 | 1.3 MB | Architecture and A/B system design source |
| `obsidian-skills` | `D:\Project Directory\Obsidian-Ecosystem\obsidian-skills` | 14 | 0.1 MB | Obsidian markdown/base/canvas/CLI skill reference |
| `screen-translation-assistant` | `D:\Project Directory\Screen-Translation-Assistant` | 90 | 0.4 MB | OCR sidecar and local desktop workflow reference |
| `ai-agent-tools-codex` | `D:\Project Directory\AI-Agent-Tools\codex` | 5197 | 47.9 MB | Codex architecture reference |
| `ai-agent-tools-openharness` | `D:\Project Directory\AI-Agent-Tools\OpenHarness` | 480 | 12.0 MB | Python CLI/MCP agent reference |
| `ai-agent-tools-ponytail` | `D:\Project Directory\AI-Agent-Tools\ponytail` | 137 | 1.3 MB | Skills/hooks/plugin packaging reference |
| `claw-code` | `D:\Project Directory\claw-code` | 364 | 11.3 MB | Rust agent harness reference |
| `claude-code-artifacts` | `D:\Project Directory\ClaudeCode` | 1261 | 54.3 MB | Local research artifact only; do not promote code directly |
| `unlimited-ocr` | `D:\Project Directory\OCR\Unlimited-OCR` | 5 | 90.8 MB | OCR artifact/PDF/wheel reference |

## Exclusions

The copy process excluded generated, private, or heavy dependency state:

```text
.git
node_modules
.venv
venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
.next
dist
build
target
data
database
logs
.cache
.turbo
coverage
.port_sessions
.omx
.env
.env.*
*.db
*.sqlite
*.sqlite3
*.log
*.pyc
*.pyo
*.tmp
*.sst
```

Post-copy scan found:

```text
BadDirectoryHits: 0
BadFileHits: 0
```

## Promotion Rule

These snapshots are preservation copies, not active runtime code. Any useful source must still be promoted through:

```text
Source snapshot
  -> Intake card
  -> Contract mapping
  -> Minimal runtime patch
  -> Tests
  -> Verification
```

The active integration plan is:

```text
workspace/intake/008_external_project_integration_plan.md
```

## Cleanup Note

After confirming the local snapshots are complete enough, `D:\Project Directory` can be cleaned manually. Do not delete source projects from D: through an agent action unless the exact target paths and impact are confirmed separately.
