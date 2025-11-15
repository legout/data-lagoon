## Why

The initial implementation of `write_dataset` / `read_dataset` uses low-level Parquet APIs (`pyarrow.parquet.write_table`, `pyarrow.parquet.read_table`) that only handle single files. This approach limits scalability (no partitioning), diverges from the spec’s intent to lean on the Arrow Dataset abstraction, and complicates the transition to upcoming changes (storage layer, statistics, pruning). PyArrow already provides `dataset.write_dataset` and `dataset.dataset` for managing multi-file datasets consistently across filesystems. We should refactor the basic write/read layer to rely on these APIs now, so later changes can build on a common foundation.

## What Changes

- Update `dataset-write` capability to require use of PyArrow Dataset APIs for writing data (even for the basic change).
- Update `dataset-read` capability to specify that reads construct a `pyarrow.dataset.Dataset` (or `FileSystemDataset`) rather than manually reading individual Parquet files.
- Refactor implementation in `src/data_lagoon/dataset.py` to:
  - Normalize data to Arrow tables/readers.
  - Use `pyarrow.dataset.write_dataset` for writing, supporting multiple files/partitions in the future.
  - Use `pyarrow.dataset.dataset` (or `FileSystemDataset.from_fragments`) for reads, returning either a Dataset handle or a materialized table.
  - Maintain compatibility with existing return types (`pa.Table`) but build from the Dataset API.
- Ensure catalog metadata still records written files and versions, but file discovery leverages `write_dataset`’s `write_options.file_visitor` to capture per-file details.

## Impact

- Specs affected: `dataset-write` (MODIFIED), `dataset-read` (MODIFIED).
- Code: `src/data_lagoon/dataset.py`, helper utilities for dataset references, tests.
- Future changes (storage layer, statistics) become simpler because we already rely on the dataset API.
