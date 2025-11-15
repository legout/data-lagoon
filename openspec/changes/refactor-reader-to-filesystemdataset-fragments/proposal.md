## Why

The current pruning-aware reader stitches together results by:
- Consulting the catalog (`files`, `row_groups`, `partitions`) to decide which files/row groups to keep.
- Reading those Parquet files directly with `pyarrow.parquet.ParquetFile` and manually concatenating tables.

This works functionally but diverges from both the OpenSpec design and established best practice in the Arrow ecosystem:
- OpenSpec for `add-predicate-and-partition-pruning-reader` explicitly calls for constructing a PyArrow **FileSystemDataset** from **ParquetFragments**, with pruning expressed via `partition_expression` and Arrow `Expression` filters.
- Delta Lake’s `DeltaTable.to_pyarrow_dataset` approach shows the intended pattern: build a `pyarrow.dataset.Dataset` backed by a filesystem, and rely on Arrow’s internal pruning and predicate pushdown when materializing via `.to_table(filter=...)` rather than hand-rolling a scan loop. citeturn0search4turn0search5

We should refactor the reader so that:
- All reads go through a **FileSystemDataset** constructed from **ParquetFragments**.
- Row-group statistics and partition metadata from the catalog are converted into Arrow `Expression`s and `partition_expression`s attached to fragments.
- Filtering is driven by PyArrow’s dataset engine (`to_table(filter=...)`), not by custom ParquetFile loops.

## What Changes

- Introduce a new pruning-aware reader pipeline that:
  - Uses catalog metadata to compute fragment-level and row-group–level pruning, but encodes that as Arrow expressions.
  - Builds `pyarrow.dataset.ParquetFragment`s for each selected file, with:
    - `row_groups` narrowed to the candidate set.
    - A `partition_expression` that captures partition key/value predicates and (where possible) statistics-derived constraints.
  - Creates a `pyarrow.dataset.FileSystemDataset` via `FileSystemDataset.from_fragments` and materializes data with `.to_table(filter=...)`.
- Align predicate representation with PyArrow’s `Expression` API so callers can pass either:
  - Our existing `(column, op, value)` triples, or
  - A pre-built `pyarrow.dataset.Expression`.
- Update the `dataset-read`, `statistics-pruning`, and `partition-pruning` specs to require this fragment-based FileSystemDataset approach rather than a bespoke ParquetFile loop.

## Impact

- Affected specs:
  - `dataset-read` (MODIFIED)
  - `statistics-pruning` (MODIFIED)
  - `partition-pruning` (MODIFIED)
- Code:
  - `src/data_lagoon/dataset.py` (read path, predicate handling, dataset construction).
  - `src/data_lagoon/catalog.py` (helper(s) to surface row-group stats and partition info in a fragment-friendly way).
- This change supersedes parts of `add-predicate-and-partition-pruning-reader` that were implemented using direct Parquet reads instead of FileSystemDataset/ParquetFragments; the spec will be clarified to match the new approach.

