## Context
- Tombstone semantics introduced earlier need explicit cleanup (vacuum) and recovery flow after crashes.
- Applies across storage backends.

## Goals
- Provide `vacuum(dataset_ref, retain_hours=...)` API that removes tombstoned/unreferenced files older than retention.
- Provide recovery routine (run at startup or on-demand) that reconciles catalog vs storage (mark stray files, clean incomplete records).
- Emit logs/metrics summarizing actions.

## Design Overview

### Tombstone Model Recap
- Files written but not referenced by any committed version are tombstones.
- Catalog may mark `files.is_tombstoned = 1` or simply lack entries.
- Recovery needs to detect both storage-only files and catalog entries flagged tombstoned.

### Vacuum Flow
1. Query catalog for tombstoned files older than retention threshold.
2. For each file, delete via storage abstraction.
3. Remove catalog rows (or mark as deleted) to keep tables slim.
4. Log counts (`deleted`, `retained_due_to_retention`, `errors`).

### Recovery Flow
1. List files under dataset `base_uri`.
2. Compare against catalog `files` for latest version(s).
3. For unreferenced files:
   - Insert catalog entry with `is_tombstoned=1` if not present.
   - Optionally move to quarantine prefix? (future enhancement)
4. For catalog entries referencing missing storage files:
   - Log warning; user may need to restore from backup.

### API Surface
- `vacuum(dataset_ref, *, retain_hours=24, catalog_uri=...)`
- `recover_catalog(dataset_ref, *, catalog_uri=..., dry_run=False)`

### Observability
- Use logging interface or return structured result object:
  ```python
  VacuumResult(deleted_files: list[str], retained_files: list[str], errors: list[str])
  ```

## Risks
- Deleting wrong files due to catalog/storage inconsistency → rely on retention period to reduce risk.
- Large datasets may make recovery expensive → allow `dry_run` and limit to recent versions.

## Open Questions
- Should vacuum support parallel deletion? Possibly later.
- Where to store retention policy? Per dataset configuration or global setting?
