## Context
- Basic read/write code still assumes local filesystem paths (`pathlib.Path(...)`), preventing us from using object stores.
- PyArrow Dataset APIs already accept an arbitrary filesystem argument (compatible with `fsspec`) so we can write/read remote locations.
- Existing `storage-backends` change describes the long-term approach; this design brings that capability forward into the dataset module.

## Goals
- Abstract dataset `base_uri` resolution into a reusable helper that returns `(filesystem, root_path)` using `fsspec`.
- Support at least: local files, S3 (`s3://`), GCS (`gs://`), Azure Data Lake/Blob (`abfs://`, `abfss://`).
- Ensure file URIs stored in the catalog retain their scheme so readers know which filesystem to use.
- Surface configuration hooks for credentials (env vars, config dict).

## Design Overview

### Storage Abstraction
- Add `storage.py` with:
  ```python
  class FileSystemHandle(NamedTuple):
      filesystem: fsspec.AbstractFileSystem
      root_path: str  # normalized path relative to filesystem
  def resolve_filesystem(base_uri: str, **options) -> FileSystemHandle:
      ...
  ```
- Use `fsspec.url_to_fs` to parse the URI and return filesystem + path.
- Provide helper to join version directories, check existence, etc.

### Write Flow Updates
- Replace `Path(...).mkdir()` with filesystem-aware directory creation (`fs.makedirs` if available).
- Call `ds.write_dataset(..., filesystem=fs, base_dir=root_path)`.
- File visitor receives relative paths; combine with filesystem/storage info to produce normalized URIs stored in catalog (e.g., `s3://bucket/path/file.parquet`).

### Read Flow Updates
- When retrieving file paths from catalog, parse scheme and obtain filesystem handle.
- Call `ds.dataset(paths, format="parquet", filesystem=fs)` so data is streamed from remote storage.

### Configuration
- Extend `DatasetRef` or API parameters to accept `storage_options` dict (forwarded to `fsspec`).
- Document environment variables / credential handling.

## Risks / Mitigations
- Additional dependency on `fsspec` (and optional `s3fs`, `gcsfs`, `adlfs`): mark as extras and fail with helpful error if missing.
- Credential leaks via catalog URIs: store only paths, keep secrets in configuration.
- Some filesystems (e.g., Azure) require asynchronous clients; use sync wrappers provided by `adlfs`.

## Relation to Existing Changes
- Complements the existing `add-parquet-storage-layer-and-file-naming` proposal by actually implementing the filesystem layer sooner.
- Later changes (statistics, pruning, vacuum) can reuse the same abstraction without further refactors.
