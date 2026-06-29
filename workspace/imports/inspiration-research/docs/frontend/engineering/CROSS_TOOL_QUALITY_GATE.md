# Cross Tool Quality Gate

## Required Gates

- Repository health: `python scripts/health_check.py`
- Backend tests: targeted pytest suite for API and agent systems.
- Frontend static gates: lint, typecheck, route validators, and production build.
- Browser check: smoke pages across key user flows.
- Desktop check: Electron pack or start command when desktop files changed.

## Failure Policy

Fix the first real failing contract. Do not skip validation scripts unless the script itself is wrong and patched with a clear reason.
