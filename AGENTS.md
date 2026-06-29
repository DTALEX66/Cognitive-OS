# AGENTS.md - Cognitive-OS Agent Operating Guide

This file is the public, sanitized operating configuration for Codex/agent work inside this repository. It describes how an agent should work on Cognitive-OS without exposing local credentials, private keys, tokens, machine-specific secrets, or personal files.

## 1. Project Mission

Cognitive-OS is the front runtime for two primary systems:

| System | Role | Current Relationship |
| --- | --- | --- |
| Knowledge-Base | A system for understanding, structure, memory, learning, review, and knowledge reuse | Receives `KB` routed material |
| Inspiration-Research | B system for research, comparison, inspiration, framework design, and strategy | Receives `IR` routed material |
| Cognitive-OS | Front operating layer that routes information, runs tasks, stores traces, evaluates results, and forms machine lessons | This repository |
| Obsidian | Upstream capture/source layer for a subset of KB inputs | Not the whole system |

The target cognition loop is:

```text
information -> attention -> understanding -> structure -> memory -> learning -> action -> feedback
```

## 2. Configuration Categories

| Category | Repository Location | Purpose |
| --- | --- | --- |
| Runtime settings | `config/settings.yaml` | App thresholds, execution defaults, memory backend |
| Model settings | `config/models.yaml` | Current model/embedding provider placeholders |
| Tool registry | `config/tools.yaml` | Tool names and risk levels |
| Agent profile | `config/agent_profile.yaml` | Public agent behavior, safety, upload, and workflow policy |
| Human/agent guide | `AGENTS.md` | Readable operating rules for Codex and future agents |
| Configuration index | `workspace/configuration/README.md` | Catalog of public vs private configuration categories |
| Intake history | `workspace/intake/` | Stepwise design and implementation log |

## 3. Safety Rules

- Work inside the current repository unless the user explicitly names another exact project path.
- Do not access `E:\` unless the user explicitly confirms the exact path, action, and impact range.
- Do not upload or print secrets: `.env`, `.codex`, SSH private keys, API keys, tokens, cookies, credentials, or password files.
- Do not commit runtime memory, local caches, virtual environments, logs, or generated databases.
- Do not randomly place, copy, export, upload, or scatter repository content, imported snapshots, runtime data, source archives, or user files outside approved project paths.
- Do not let generated data spill outside project-owned paths such as `data/`, `workspace/local-imports/`, or an explicitly approved output directory.
- Prefer small, auditable changes that can be reverted with one commit.
- Do not use destructive actions such as recursive deletion, hard reset, forced push, or mass overwrite unless the user separately confirms scope.

## 3.1 Data Boundary Rules

- Default data posture is local-only, project-contained, and no-egress.
- Treat `workspace/local-imports/`, `data/`, `.venv/`, `.codex/`, external source snapshots, and imported reference folders as contained local data.
- Before copying data across roots, state the source path, target path, exclusion rules, and whether the target is ignored by Git.
- Before creating generated outputs, choose the narrowest approved destination: `data/output/` for runtime output, `workspace/intake/` for planning records, `workspace/local-imports/` for ignored local snapshots, or a user-approved exact path.
- Exclude secrets, credentials, runtime databases, logs, caches, dependency folders, build outputs, model weights, browser data, and private local state from copied snapshots.
- Network calls that include local file content, source code, traces, memory records, or imported snapshots require explicit user approval for that exact destination and payload class.
- Generated files should stay under the current repository or approved temp directories. Do not write to sibling project folders, cloud-sync folders, other drives, or user profile locations without confirmation.
- If a task needs export or upload, prefer a minimal, redacted artifact over raw folders or broad archives.

## 4. Git Rules

Before modifying repository files:

```powershell
git status --short
```

After modifying repository files:

```powershell
git diff --stat
git status --short
```

Upload policy:

- Use explicit paths when staging files.
- Avoid `git add .`.
- Do not commit or push unrelated local changes.
- Do not force push.
- Commit messages should describe the functional scope.
- Repository text files must be UTF-8 without BOM.
- Do not use lossy text handling such as `errors="ignore"` for upload-critical reads.
- Before upload, run the encoding audit test and reject files that fail UTF-8 decoding or contain replacement characters/mojibake markers.
- On Windows, do not trust garbled PowerShell display alone; verify bytes with an explicit UTF-8 reader before rewriting text.
- In Windows PowerShell, use `Get-Content -Encoding UTF8` for repository text. Do not use default `Get-Content` for Chinese or mixed-language files.
- Do not use PowerShell text write commands for repository files unless UTF-8 no-BOM behavior has been verified; prefer Python or editor saves with UTF-8 no BOM.
- If Git push over HTTPS fails or resets, use the repository SSH remote and run the environment doctor before retrying.
- Repository-local Git should use `core.autocrlf=false`, `core.eol=lf`, and UTF-8 commit/log encodings.

Environment setup:

```powershell
.\scripts\setup_env.ps1
.\.venv\Scripts\python.exe scripts\doctor_environment.py --fix
```

## 5. Network Rules

- Default work should be local.
- Network access is allowed when the user asks to pull, push, clone, verify remote status, or fetch current external information.
- GitHub remote for this repository is expected to use SSH:

```text
git@github.com:DTALEX66/Cognitive-OS.git
```

## 6. Implementation Workflow

For each implementation round:

1. Confirm repository status.
2. Read the relevant files first.
3. Make the smallest coherent change.
4. Add an intake note under `workspace/intake/` when the change affects framework direction.
5. Run the smallest useful verification.
6. Report what changed, what was tested, what remains uncertain, and how to roll back.

## 7. Current System Boundaries

- File ingestion v1 only reads files inside the Cognitive-OS project root.
- Supported file extensions are `.md`, `.markdown`, and `.txt`.
- Directory ingestion defaults to `*.md` and caps the number of files.
- High-risk content routes to `REVIEW` before action.
- Current tool execution is conservative and uses a risk registry.

## 8. Private Configuration Not Stored Here

The following must stay local and must not be committed:

- Real Codex desktop settings and session state
- SSH private keys and GitHub credentials
- API keys and model provider credentials
- `.env`, `.npmrc`, `.pypirc`, cookies, and browser data
- Local Obsidian vault paths unless the user explicitly chooses a project-local import/export path
- Runtime `data/`, memory stores, logs, caches, and virtual environments

## 9. Codex Configuration

Codex-specific public configuration is stored in:

| File | Purpose |
| --- | --- |
| `config/codex_profile.yaml` | Machine-readable Codex behavior profile |
| `.codex.example/config.example.toml` | Safe example local config template |
| `workspace/configuration/CODEX.md` | Human-readable Codex configuration guide |

The real `.codex/` directory is private local state and must not be committed.
