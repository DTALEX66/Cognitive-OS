# Privacy Security Compliance Spec

## Local First

User knowledge, route data, training records, API keys, and sync state stay local unless the user explicitly exports or syncs them.

## Sensitive Data

- Never display API secrets after creation except the one-time creation result.
- Mark sync and export actions clearly.
- Do not auto-upload local route assets.

## Desktop

The EXE shell must load local or configured URLs only and should keep privileged Electron APIs isolated behind preload.
