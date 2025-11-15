## Why

To provide ACID-style semantics, the library must ensure that concurrent writers do not corrupt the catalog or expose partial data, and that readers always see a consistent snapshot version. The current specs define catalog structures and basic write/read behavior, but they do not fully specify how transaction versions are assigned, how conflicts between writers are detected, or how locks are used to guarantee atomic catalog updates. This change introduces a transaction and concurrency model aligned with the PRD and technical spec’s optimistic concurrency approach.

## What Changes

- Introduce a `transactions-and-concurrency` capability that:
  - Defines a versioned transaction log model where each successful commit increments a dataset-level version number.
  - Specifies how writers check the current version before committing and detect conflicts (optimistic concurrency control).
  - Defines how database transactions and locks (e.g., advisory locks for PostgreSQL, exclusive transactions for SQLite/DuckDB) are used to prevent conflicting catalog updates.
  - Clarifies crash behavior: failed writes do not advance the version and only leave tombstoned files in storage.
- Modify `dataset-write` so that:
  - Writes occur within a single database transaction that updates `transactions`, `files`, `row_groups`, and `datasets.current_version` atomically.
  - Writers compare their expected base version to the current version and fail with a conflict error if it has changed.
- Modify `dataset-read` so that:
  - Reads use a stable version (either explicitly provided or the `current_version` at read start).
  - Readers are isolated from in-flight catalog updates and never observe partial writes.

## Impact

- Affected specs:
  - `transactions-and-concurrency` (new)
  - `dataset-write` (MODIFIED)
  - `dataset-read` (MODIFIED)
- Builds on existing specs:
  - `catalog-store` (`transactions`, `files`, `row_groups`, `datasets.current_version`)
  - `file-naming-and-tombstones` (tombstone semantics for failed writes)
- Affected code (future implementation):
  - Transaction manager module that encapsulates version handling and locking.
  - Changes to write and read paths to use this transaction manager.

