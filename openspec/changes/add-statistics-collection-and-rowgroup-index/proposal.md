## Why

To support efficient predicate pruning and time-travel reads, the system must collect detailed file- and row-group-level statistics at write time and persist them in the catalog. The current specs define catalog tables and basic writes, but they do not yet require how statistics are captured from DuckDB (`RETURN_STATS`) or PyArrow (`file_visitor`) nor how row groups and partitions are indexed. This change introduces explicit requirements for statistics collection and row-group/partition indexing so later changes can rely on this metadata for optimized reads.

## What Changes

- Introduce a `statistics-collection` capability that:
  - Defines how write operations using DuckDB’s `COPY ... RETURN_STATS` capture per-file and per-column statistics.
  - Defines how write operations using PyArrow’s `dataset.write_dataset(..., file_visitor=...)` extract row-group and column statistics from `parquet.FileMetaData`.
  - Requires storing file-level metrics (row counts, sizes) and row-group statistics (per-column min, max, null counts) in the catalog.
- Introduce a `row-group-index` capability that:
  - Specifies how `row_groups` records are created and linked to `files`.
  - Specifies how partition key/value pairs are stored in the `partitions` table.
  - Ensures that row-group and partition metadata are queryable by dataset and version for later pruning logic.
- Keep read behavior unchanged for now; use of these statistics for pruning is introduced in a subsequent change.

## Impact

- Affected specs:
  - `statistics-collection` (new)
  - `row-group-index` (new)
- Builds on existing specs:
  - `catalog-store` (tables for `files`, `row_groups`, `partitions`)
  - `dataset-write` (write operations that will now populate statistics)
- Affected code (future implementation):
  - DuckDB-based writer that parses `RETURN_STATS` output.
  - PyArrow-based writer that uses `file_visitor` and `FileMetaData`.
  - Catalog persistence layer for row-group and partition records.

