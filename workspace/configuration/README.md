# Configuration Catalog

This folder documents the public configuration that is safe to keep in the Cognitive-OS repository. It does not include local Codex session data, credentials, model provider secrets, SSH keys, or machine-specific private settings.

## Public Configuration

| Category | Files | Audience | Notes |
| --- | --- | --- | --- |
| Agent operating guide | `AGENTS.md` | Human + agent | Main rules for safe Codex/agent work |
| Agent machine profile | `config/agent_profile.yaml` | Agent + scripts | Structured, public, sanitized configuration |
| Runtime app settings | `config/settings.yaml` | App runtime | Thresholds, dry-run defaults, memory backend |
| Model placeholders | `config/models.yaml` | App runtime | Stub/local placeholder providers for now |
| Tool risk registry | `config/tools.yaml` | App runtime | Tool risk categories and default dry-run behavior |
| Intake records | `workspace/intake/*.md` | Human + agent | Step-by-step implementation history |
| Imported reference assets | `workspace/imports/**` | Human + agent | Selected reusable KB/IR material, not active runtime state |

## Private Configuration Not Uploaded

| Category | Examples | Reason |
| --- | --- | --- |
| Credentials | SSH private keys, GitHub tokens, API keys | Secret material |
| Local Codex state | `.codex`, desktop session state, local MCP credentials | Machine/session specific |
| Environment files | `.env`, `.npmrc`, `.pypirc` | Often contains secrets |
| Runtime data | `data/memory`, logs, traces, cache, SQLite files | Generated local state |
| External vault paths | Personal Obsidian vault absolute paths | Personal filesystem data |

## Configuration Boundaries

- `AGENTS.md` describes how future agents should behave in this repository.
- `config/agent_profile.yaml` mirrors the same policy in a structured form.
- Runtime configuration under `config/` should stay generic until real providers and deployment environments are chosen.
- Private values should be injected through local environment files that remain ignored by Git.

## Next Configuration Work

1. Add environment-specific examples such as `.env.example` without real secrets.
2. Add ingestion profiles for `obsidian`, `knowledge-base`, and `inspiration-research`.
3. Add router evaluation samples under a dedicated non-secret test fixture directory.
4. Add CI checks for compile, import, and basic API smoke tests.
