## Why

`write_dataset` currently writes all rows into a flat directory. The spec and user stories call for partitioning datasets by one or more columns (e.g., `date`, `region`) so that data lands in directory structures like `date=2024-01-01/region=us/part-...parquet`. Without partitioned writes, downstream pruning (partition pruning + statistics) cannot skip entire directories, and users cannot organize data by common filters. We must add partitioning support to the dataset module so callers can specify partition keys and the catalog can record the resulting partition metadata for each file.

## What Changes

- Extend `write_dataset` with a `partition_by` argument (list of column names or partition expressions) passed to `pyarrow.dataset.write_dataset`.
- Update the storage layout so each write creates per-version subdirectories containing Hive-style partition directories.
- Ensure the file visitor captures partition key/value pairs (either from PyArrow’s partition descriptors or by parsing the path) and persists them via the catalog helper.
- Update specs (`dataset-write`, `partition-pruning`) to state that partitioned writes are supported and that partition metadata is always stored.

## Impact

- Affected specs: `dataset-write` (MODIFIED), `partition-pruning` (MODIFIED).
- Code: dataset writer options, storage helper (directory creation), catalog metadata persistence.
- Tests: new cases verifying partitioned writes create the expected directory layout and catalog entries.
