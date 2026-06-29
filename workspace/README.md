# Cognitive-OS Workspace

This workspace keeps reusable assets from the two source projects without mixing them directly into the runnable app.

## Source Projects

- `Knowledge-Base`: current runnable engineering system and code references.
- `Inspiration-Research`: research, framework, A/B system design, bridge docs, and intake planning.

## Layout

```text
workspace/imports/
  inspiration-research/
    root/                    # project rules and bridge docs
    docs/                    # current IR framework docs
    maps/                    # A/B mapping
    reference-key-docs/      # selected integration/reference docs
    dual-system-integration/ # A/B integration analysis
    a-line-design/           # selected Human Learning OS design docs
    b-line-design/           # Machine/Agent OS design docs
  knowledge-base/
    root/                    # repo-level README/INSTALL/AGENTS
    project-docs/            # KB project docs and manifest/status
    code-reference/          # selected backend modules for reference
    frontend-reference/      # frontend config reference
```

## Rules

- Treat imported files as reference assets first, not active runtime code.
- Promote assets into the root app only through an Intake Card or implementation task.
- Do not copy `.git`, databases, caches, build outputs, node_modules, or private data.
- Keep Obsidian as a partial upstream input source only; it is not the main system.
