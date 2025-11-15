## Why

The current dataset writer persists only minimal metadata (path, row count, size) for each Parquet file. The PRD and later changes (statistics-based pruning, schema evolution, partition pruning) expect the catalog to contain the full Parquet file metadata: schema version, row-group statistics, column-level min/max/null counts, and partition key/value pairs. Instead of deferring this to a later “statistics” feature, we should capture the metadata directly from PyArrow’s `WrittenFile.metadata` every time `write_dataset` runs so the catalog remains authoritative and read paths never need to re-open Parquet footers.

## What Changes

- Enhance the `file_visitor` callback to extract `pyarrow.parquet.FileMetaData` for each file (using `.to_dict()` for easy serialization), including:
  - Row-group info (row counts, byte sizes).
  - Column chunk statistics (min/max/null counts).
  - Schema fingerprint (to map files to `schema_versions`).
- Persist this metadata:
  - Extend catalog helpers to insert into `schema_versions`, `files`, `row_groups`, and `partitions` tables in one step.
  - Store a flag indicating whether complete statistics were captured.
- Update `WriteResult` / logging so callers can inspect captured metadata if desired.
- Ensure existing specs (`statistics-collection`, `dataset-write`) explicitly require this behavior.

## Impact

- Affected specs: `statistics-collection` (MODIFIED), `dataset-write` (MODIFIED).
- Code: `src/data_lagoon/dataset.py`, catalog helpers, possibly new serialization utilities.
- Tests: add coverage verifying that catalog entries contain expected stats/partition entries after a write.
