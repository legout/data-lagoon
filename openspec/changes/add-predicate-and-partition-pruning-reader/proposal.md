## Why

To meet the performance goals in the PRD, reads must avoid scanning all Parquet files and row groups for a dataset when filters are selective. The catalog now stores file- and row-group-level statistics and partition metadata, but the `dataset-read` capability still constructs datasets using all files for a version. This change introduces a pruning-aware reader that uses catalog statistics and partitions to select only relevant files and row groups before building a PyArrow dataset, while preserving snapshot semantics and engine interoperability.

## What Changes

- Modify the `dataset-read` capability so that:
  - `read_dataset` uses catalog statistics and partitions (when available) to select a subset of files and row groups for a given dataset version, based on caller predicates.
  - The reader maintains snapshot semantics: all visible data for the given version that may satisfy the predicate is included; no data from other versions is included.
  - If statistics are unavailable or incomplete, the reader safely falls back to scanning more files or row groups rather than returning incorrect results.
- Introduce a `statistics-pruning` capability that:
  - Specifies how predicates are translated into catalog queries over `row_groups` and `files`.
  - Defines how row-group-level statistics (min/max/null counts) are used to decide whether a row group can be skipped.
- Introduce a `partition-pruning` capability that:
  - Specifies how partition key/value metadata is used to exclude entire files that cannot satisfy the predicates.
  - Defines combined use of partition filters and statistics filters for optimal pruning.

## Impact

- Affected specs:
  - `dataset-read` (MODIFIED)
  - `statistics-pruning` (new)
  - `partition-pruning` (new)
- Builds on existing specs:
  - `row-group-index` (row-group statistics in catalog)
  - `storage-backends` and `file-naming-and-tombstones` (locating files)
- Affected code (future implementation):
  - Reader that issues catalog queries to select files/row groups.
  - Logic to construct `ParquetFragment`s and a `FileSystemDataset` with appropriate filters/partition expressions.
  - Integration points with DuckDB, Polars, and DataFusion that benefit from pre-pruned file lists.

