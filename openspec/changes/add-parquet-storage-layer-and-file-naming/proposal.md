## Why

The project needs a clear, backend-agnostic storage layer and a consistent file-naming strategy before layering on statistics, pruning, and advanced concurrency features. Today, datasets are specified by `base_uri`, but there is no canonical way to map those URIs to local disks or object stores, and no guarantee that Parquet files are named in a way that supports uniqueness, ordering, and tombstone handling. This change introduces a storage abstraction (via a filesystem layer such as `fsspec`) and a UUID v7-based naming scheme aligned with the technical spec.

## What Changes

- Introduce a `storage-backends` capability that:
  - Defines how dataset `base_uri` values map to concrete filesystems using a common abstraction (e.g., `fsspec`).
  - Requires support for local files (`file://` or bare paths) and major object stores (at least S3, GCS, and Azure Data Lake / Blob Storage).
  - Specifies how paths are constructed for Parquet files under a dataset’s `base_uri`.
- Introduce a `file-naming-and-tombstones` capability that:
  - Requires Parquet files to be named using UUID v7-based patterns for uniqueness and timestamp ordering.
  - Clarifies that the catalog is the source of truth: only files referenced in the catalog are considered part of any version; unreferenced files are tombstones.
  - Establishes that write operations do not rely on temporary directories; atomicity is achieved via the catalog and tombstone semantics.
- Align existing `dataset-write` behavior with these capabilities without yet introducing statistics-based pruning or full concurrency control.

## Impact

- Affected specs:
  - `storage-backends` (new)
  - `file-naming-and-tombstones` (new)
- Builds on existing specs:
  - `dataset-core` (dataset `base_uri`)
  - `catalog-store` (files and versions tables)
  - `dataset-write` (writes Parquet files under `base_uri`)
- Affected code (future implementation):
  - Storage abstraction module (e.g., `data_lagoon.storage`) that wraps `fsspec`-compatible filesystems.
  - File-path and file-name generation used by write operations.
  - Any maintenance code that inspects or cleans up tombstoned files.

