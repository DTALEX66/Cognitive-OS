# Coding Standards

## TypeScript

- Prefer typed data contracts over ad hoc `any`.
- Keep page components thin and move workflow logic into components or libs.
- Do not create placeholder components that render empty states only.
- Keep imports resolvable through `@/` aliases.

## Data

- Route fixtures must contain real nodes, questions, answers, memory images, and visual mappings.
- JSON must be UTF-8 without BOM.
- Text source files use LF line endings.

## Validation

Before handoff run: `npm run lint`, `npm run typecheck`, `npm run test`, and `npm run build`.
