## Why

After refactoring the basic `write_dataset`/`read_dataset` flows to rely on the PyArrow Dataset API, the remaining gap is storage backends: we still assume a local filesystem path and call `Path(...).mkdir()` + `dataset.dataset(file_paths, format="parquet")`. The PRD and existing specs call for supporting remote object stores (S3, GCS, ADLS) via `fsspec`. Without an abstraction that resolves dataset URIs to `fsspec` filesystems, we cannot correctly write to or read from those stores, nor can we reuse PyArrow’s dataset APIs across schemes. This change introduces the storage layer now instead of waiting for later enhancements, aligning the dataset module with the storage-backends requirements.

## What Changes

- Add a storage abstraction (e.g., `storage.py`) that:
  - Parses dataset `base_uri` and returns the corresponding `fsspec` filesystem + path.
  - Provides helpers for ensuring directories exist (where meaningful) and for constructing dataset paths rooted in remote buckets.
- Update `write_dataset` and `read_dataset` to use this abstraction:
  - Writers call `ds.write_dataset(..., filesystem=fs, base_dir=path)` so PyArrow writes remotely.
  - Readers call `ds.dataset(..., filesystem=fs)` using catalog-stored URIs.
- Support S3 (`s3://`), GCS (`gs://`), Azure (`abfs://`, `abfss://`), plus local filesystem fallback.
- Ensure dataset references can include credentials/config via environment variables or `fsspec` kwargs.

## Impact

- Specs: `storage-backends/spec.md` (MODIFIED to say dataset module must use fsspec), `dataset-write/spec.md` (MODIFIED to mention filesystem abstraction).
- Code: new storage helper module, updates to `dataset.py`, potential adjustments in catalog to store normalized URIs.
- Future changes (statistics, pruning) benefit from consistent remote path handling.
