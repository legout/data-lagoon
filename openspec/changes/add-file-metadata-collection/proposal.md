## Why

Even after switching to `pyarrow.dataset.write_dataset`, the dataset module currently records only file path, size (best-effort), and row count per file. The PRD, statistics change, and downstream pruning features all depend on capturing richer metadata (row-group stats, schema versions, partition values) via the dataset writer’s metadata hooks. Rather than waiting for the full statistics change, we should ensure every write collects and persists as much metadata as PyArrow exposes so the catalog is immediately useful to readers, engine integrations, and administrative tooling.

## What Changes

- Enhance the file visitor to extract:
  - Row-group-level stats (`min`, `max`, `null_count`) per column (when available).
  - Partition key/value pairs derived from directory structure or writer options.
  - Schema fingerprint to link files to the `schema_versions` table.
- Persist this metadata via catalog helpers (e.g., extend `record_basic_write` or introduce a dedicated metadata writer) so that future changes don’t need to backfill older versions.
- Update `WriteResult` (and potentially return types) to expose captured metadata for caller introspection.

## Impact

- Specs: `statistics-collection/spec.md` (MODIFIED to say basic writes already emit row-group stats), `dataset-write/spec.md` (MODIFIED to require metadata capture).
- Code: dataset module visitor, catalog helper, new serialization utilities.
- Tests verifying metadata persistence and availability via catalog queries.
