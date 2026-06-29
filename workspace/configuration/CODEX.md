# Codex Configuration

This page records the public, sanitized Codex configuration for Cognitive-OS. It is a project-level template, not the real local Codex app state.

## What Was Uploaded

| Category | Files | Purpose |
| --- | --- | --- |
| Codex public profile | `config/codex_profile.yaml` | Machine-readable policy for Codex behavior in this repository |
| Codex local template | `.codex.example/config.example.toml` | Portable example for recreating safe local defaults |
| Codex template README | `.codex.example/README.md` | Explains what the template is and what must stay private |
| Configuration guide | `workspace/configuration/CODEX.md` | Human-readable classification of Codex config |

## What Was Not Uploaded

| Private Item | Why It Stays Local |
| --- | --- |
| Real `.codex/` directory | May contain local session state, tool state, credentials, connector metadata, or machine-specific paths |
| API keys and model provider credentials | Secret material |
| SSH private keys and GitHub tokens | Secret material |
| Browser cookies or connector account tokens | Personal account access |
| Absolute personal Obsidian vault paths | Personal filesystem information |
| Local runtime data | Generated state, not source configuration |

## Codex Configuration Layers

| Layer | Role | Status |
| --- | --- | --- |
| Repository guide | `AGENTS.md` | Uploaded |
| General agent profile | `config/agent_profile.yaml` | Uploaded |
| Codex-specific profile | `config/codex_profile.yaml` | Uploaded |
| Example local config | `.codex.example/config.example.toml` | Uploaded as template |
| Real local config | `.codex/` or user profile Codex config | Not uploaded |

## Recommended Local Setup Pattern

1. Keep project source in the repository.
2. Keep real credentials and account links in local-only Codex settings or environment files.
3. Use `.codex.example/config.example.toml` only as a reference template.
4. Do not rename `.codex.example` to `.codex` inside the repository unless you understand what will be stored there.
5. If a local `.codex/` directory exists, Git should ignore it.

## Classification

| Config Type | Commit? | Example |
| --- | --- | --- |
| Public project policy | Yes | `AGENTS.md`, `config/codex_profile.yaml` |
| Runtime defaults without secrets | Yes | `config/settings.yaml`, `config/tools.yaml` |
| Example-only local config | Yes | `.codex.example/config.example.toml` |
| Real local Codex state | No | `.codex/` |
| Provider credentials | No | API keys, OAuth tokens, cookies |
| Personal paths | Usually no | Real Obsidian vault absolute paths |

## Current Codex Behavior Contract

- Work inside the current repository unless the user names another exact path.
- Treat `E:/` as protected and require explicit confirmation before any access.
- Run `git status --short` before modifications.
- Run `git diff --stat` and `git status --short` after modifications.
- Use explicit Git staging paths and avoid `git add .`.
- Do not commit or print private configuration.
- Prefer local validation before network operations.
- Push only when the user asks for upload or publish.
