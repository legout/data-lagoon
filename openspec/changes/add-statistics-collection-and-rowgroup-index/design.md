## Context
- Builds on storage-backed writes to capture file-level and row-group-level metadata.
- Required for predicate/partition pruning and time-travel reads in future changes.

## Goals
- Capture statistics from DuckDB writes (`RETURN_STATS`) and PyArrow writes (`file_visitor`).
- Persist file metrics (row count, file size) and per-row-group stats (min/max/null count per column).
- Populate `row_groups` and `partitions` tables consistently across engines.

## Non-Goals
- Actual pruning logic (handled in `add-predicate-and-partition-pruning-reader`).
- Compaction/maintenance tasks (later changes).

## Design Overview

### Architecture
- Writer pipeline emits `WritePlan` containing data about each output file.
- Two sources of stats:
  1. DuckDB: `COPY ... RETURN_STATS` result set (per-file & per-column stats).
  2. PyArrow: `file_visitor` callback providing `WrittenFile` + `parquet.FileMetaData`.
- Normalize both into a shared structure:
  ```python
  FileStats(
      path: str,
      file_size: int,
      row_count: int,
      partitions: dict[str, str],
      row_groups: list[RowGroupStats],
  )
  ```

### Catalog persistence
- Add helper `CatalogWriter.persist_file_stats(dataset_id, version, file_stats_list)`.
- Inserts rows into `files`, `row_groups`, `partitions`.
- Handles missing stats by setting JSON fields to `NULL`.

### Handling Missing Stats
- Some writers (e.g., PyArrow without `write_statistics=True`) may omit stats.
- Policy: store row group record with `stats_min_json = null` etc., and mark file as “stats_incomplete”.

## Key Decisions
- Use JSON serialization for min/max/null counts as per spec.
- Keep partitions parsing logic consistent (from file paths or writer metadata).
- Accept that row-group statistics may vary between engines; store as best-effort.

## Risks
- DuckDB schema changes upstream may break parsing → pin to stable version, add tests.
- Large datasets may produce huge metadata payloads → consider batching inserts.

## Open Questions
- Should we deduplicate identical partition key/value rows? Probably not—files rarely share duplicates needing dedup.
- How to track which engine produced each file? Could add optional column for debugging.
