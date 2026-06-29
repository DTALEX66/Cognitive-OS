# Six Hour Execution Window

## Purpose

Define a supervised execution window for extended UI, data, and validation work.

## Loop

1. Run health checks.
2. Fix the first failing validation.
3. Re-run targeted checks.
4. Run full front-end validation.
5. Record remaining risk before release.

The loop stops if validation is blocked by missing credentials, external service downtime, or a destructive action requirement.
