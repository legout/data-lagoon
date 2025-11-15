## Why

The library is intended to interoperate seamlessly with DuckDB, Polars, DataFusion, and other Arrow-native engines. While the current `read_dataset` API returns a PyArrow dataset/table that can be used by these systems, users benefit from dedicated helpers that construct engine-native objects with the right pruning and partitioning semantics. This change introduces explicit engine integration capabilities and clarifies how pruning-aware datasets are handed off to each engine.

## What Changes

- Introduce an `engine-integrations` capability that:
  - Defines helper functions for constructing DuckDB relations, Polars lazy frames, and DataFusion datasets from a pruned dataset representation.
  - Specifies which features are guaranteed across engines (e.g., predicate pushdown, projection) and which are best-effort.
  - Ensures integrations reuse the same pruned file/row-group selection logic defined in previous changes.
- Modify `dataset-read` so that:
  - It clearly specifies that the primary return type is an Arrow-compatible dataset/table suitable for passing to engine helpers.
  - It defines optional convenience helpers or methods to directly obtain engine-native objects (where appropriate).

## Impact

- Affected specs:
  - `engine-integrations` (new)
  - `dataset-read` (MODIFIED)
- Builds on existing specs:
  - `dataset-read` with predicate and partition pruning
  - `statistics-pruning` and `partition-pruning`
- Affected code (future implementation):
  - Helper modules for DuckDB, Polars, and DataFusion integration.
  - Documentation and examples showing idiomatic usage with each engine.

