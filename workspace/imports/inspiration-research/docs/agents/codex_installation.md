# Installing Agents to Codex

## Prerequisites

1. Generate TOML files:
   ```bash
   python scripts/convert-agents.py --tool codex
   ```

2. Verify output:
   ```bash
   ls integrations/codex/agents/*.toml
   ```

## Install from PowerShell

Default target: `$env:USERPROFILE\.codex\agents`

```powershell
# Install all agents
.\scripts\install-agents.ps1 -Tool codex

# Install specific team
.\scripts\install-agents.ps1 -Tool codex -Team foundation

# Install specific agent
.\scripts\install-agents.ps1 -Tool codex -Agent kb-orchestrator

# Preview only
.\scripts\install-agents.ps1 -Tool codex -DryRun

# Custom destination
.\scripts\install-agents.ps1 -Tool codex -Destination "D:\custom\codex\agents"

# Overwrite existing
.\scripts\install-agents.ps1 -Tool codex -Force
```

## Install from Bash

Default target: `~/.codex/agents`

```bash
# Install all agents
./scripts/install-agents.sh --tool codex

# Install specific team
./scripts/install-agents.sh --tool codex --team foundation

# Install specific agent
./scripts/install-agents.sh --tool codex --agent kb-orchestrator

# Preview only
./scripts/install-agents.sh --tool codex --dry-run

# Custom destination
./scripts/install-agents.sh --tool codex --dest ~/my-agents

# Overwrite existing
./scripts/install-agents.sh --tool codex --force
```

## Verify Installation

```bash
# Codex agents directory should contain .toml files
ls ~/.codex/agents/*.toml

# or on Windows
Get-ChildItem $env:USERPROFILE\.codex\agents\*.toml
```

> Note: Restart Codex after installing new agents for them to take effect.
