## Why

Over time, failed or obsolete transactions will leave tombstoned files in object storage, and crashes may leave the catalog or storage in a partially reconciled state. To keep storage costs under control and maintain reliability, the system needs explicit maintenance operations to vacuum tombstones and recover clean state on startup. The current specs define tombstone semantics and transaction behavior but do not specify how or when cleanup and recovery occur. This change introduces maintenance APIs and recovery behavior aligned with the PRD’s reliability goals.

## What Changes

- Introduce a `maintenance-vacuum-and-recovery` capability that:
  - Defines a `vacuum` operation that scans for tombstoned or unreferenced files and deletes them according to configurable retention policies.
  - Defines startup or on-demand recovery behavior that reconciles catalog state with storage, marking stray files as tombstones and cleaning up incomplete catalog records when safe.
  - Specifies observability requirements (what is logged or reported) for vacuum and recovery actions.
- Modify `file-naming-and-tombstones` so that:
  - Tombstone handling is explicitly connected to the maintenance vacuum process.
  - The behavior of tombstones across crashes and restarts is clearly defined.

## Impact

- Affected specs:
  - `maintenance-vacuum-and-recovery` (new)
  - `file-naming-and-tombstones` (MODIFIED)
- Builds on existing specs:
  - `transactions-and-concurrency` (failed writes and versions)
  - `file-naming-and-tombstones` (tombstone semantics)
  - `catalog-store` (files, transactions, and version metadata)
- Affected code (future implementation):
  - Maintenance utilities for vacuuming and recovery.
  - Integration points or CLI helpers that allow operators to invoke these operations.

