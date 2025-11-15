## Context
- Current basic write/read implementation uses low-level Parquet APIs (`pq.write_table`, `pq.read_table`) and assumes a single file per version.
- The spec and upcoming changes expect us to rely on PyArrow’s Dataset API so we can add partitioning, multi-file writes, statistics collection, and engine integrations more easily.
- Switching now reduces future churn and ensures consistent metadata capture.

## Goals
- Replace direct `pyarrow.parquet.write_table` calls with `pyarrow.dataset.write_dataset`.
- Capture per-file metadata via `file_visitor` to populate the catalog (file paths, row counts, optionally stats).
- Replace `pyarrow.parquet.read_table` usage with `pyarrow.dataset.dataset(...).to_table()` (or returning the dataset handle) so downstream code can reuse the dataset object.
- Maintain backward compatibility for current API signatures and test expectations (still returning `pa.Table` by default).

## Design

### Write Path
1. Normalize input to Arrow `Table`/`RecordBatchReader`.
2. Determine output filesystem/path (still local path for now).
3. Call `ds.write_dataset(...)` with:
   - `format="parquet"`, `base_dir=base_uri`, optional `partitioning` (future).
   - `file_visitor` callback that records `WrittenFile` metadata (path, row count, schema) into a list.
4. After write completes, persist collected file metadata in catalog for the new version (`record_basic_write` may evolve to accept multiple files).

### Read Path
1. Resolve dataset + version from catalog, obtain list of file paths.
2. Construct dataset: `dataset = ds.dataset(file_paths, format="parquet")`.
3. Return dataset handle or convert to table (`dataset.to_table()`); keep optional `as_table=True` default for now.
4. This dataset object can later be passed to engine helpers without re-reading file lists.

### API Changes
- Add optional parameter `as_dataset: bool = False` to `read_dataset` to let callers request the dataset handle.
- `WriteResult` remains similar but may include dataset handle or dataset path list if useful.

## Risks / Mitigations
- `ds.write_dataset` may produce multiple files per write; catalog code must handle multiple entries (update helper accordingly).
- Need to ensure file visitor works consistently across backends; for now, local filesystem only.
- Tests must be updated to account for new file naming pattern (dataset API chooses names unless we pass `filename_template`).

## Dependencies / Follow-up
- Storage-layer change can now plug into dataset API without replacing the write logic again.
- Statistics collection change can hook into the same `file_visitor` data.
- Engine integrations can build directly atop the dataset objects returned here.
