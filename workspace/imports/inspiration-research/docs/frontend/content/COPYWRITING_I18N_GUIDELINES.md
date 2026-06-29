# Copywriting And I18n Guidelines

## Copy

- Lead with the user action.
- Use present tense for system state.
- Use plain error messages with the next action.
- Avoid visible instructional filler inside dense workspaces.

## I18n

- Keep `data/i18n/zh-CN.json` and `data/i18n/en-US.json` key-aligned.
- Add keys before wiring UI text.
- Do not mix untranslated labels in a single control group.

Every translation update must pass `node scripts/validate-i18n.mjs`.
