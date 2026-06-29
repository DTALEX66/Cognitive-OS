# Commercial Release Gate

## Required Before Release

- `npm run lint`
- `npm run typecheck`
- `npm run test`
- `npm run build`
- backend API smoke test
- Electron desktop smoke test when desktop files change

## Release Criteria

- No empty data routes.
- No missing thumbnails for built-in nodes.
- Desktop shell opens to the same usable workflow as the web app.
- Version ledger documents the release line.
