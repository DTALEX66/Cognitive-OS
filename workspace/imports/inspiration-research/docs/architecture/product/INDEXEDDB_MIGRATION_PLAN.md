# IndexedDB Migration Plan

## Purpose

Lumina AI v3.0 keeps `localStorage` as the active MVP storage layer, but prepares the project for IndexedDB so route packages, image assets, versions, and training records can grow into durable local learning assets.

## Migration order

1. Keep `localStorage` as the compatibility layer.
2. Add IndexedDB route-package persistence behind a storage adapter.
3. Migrate route packages first, then training records, then image blobs.
4. Keep export/import JSON available even after IndexedDB is enabled.
5. Never migrate by overwriting frozen route assets without user confirmation.

## Stores

```text
routePackages
imageAssets
trainingRecords
metadata
```

## Commercial rule

A confirmed or frozen route must survive browser refresh, tool switching, and app upgrades. If a migration cannot prove asset integrity, show a recovery prompt instead of silently changing user data.
