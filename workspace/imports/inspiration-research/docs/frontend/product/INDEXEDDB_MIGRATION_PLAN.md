# IndexedDB Migration Plan

## Goal

Move route packages from single-record localStorage persistence into IndexedDB while keeping existing local sessions readable.

## Current Keys

- Canonical current route key: `lumina.current.route-package.v1`
- Legacy current route key: `lumina.currentRoutePackage.v1`
- IndexedDB database: `lumina-route-assets`
- IndexedDB object store: `routePackages`

## Migration Steps

1. Read canonical local route state first.
2. If canonical data is absent, read the legacy key.
3. Save the recovered route through `saveRoutePackageToIndexedDB`.
4. Keep localStorage fallback available for browsers without IndexedDB.
5. Remove or ignore legacy data only after a valid route package is persisted.

## Verification

Run `node scripts/validate-storage-migration.mjs` and `node scripts/validate-storage-contract.mjs` before release.
