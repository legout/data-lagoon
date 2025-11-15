## Why

The project needs a simple, Pythonic way to write and read Parquet-backed datasets before adding more advanced features like statistics-based pruning, schema evolution, and concurrency control. Users should be able to append Arrow-like data to a dataset and read back a consistent snapshot using only the core dataset and catalog capabilities defined in `add-core-dataset-and-catalog`.

## What Changes

- Introduce a `dataset-write` capability that:
  - Accepts Arrow `Table`/`RecordBatchReader`, Pandas DataFrame, or Polars DataFrame as input.
  - Normalizes inputs to Arrow and writes Parquet files under the dataset’s `base_uri`.
  - Records basic file metadata and a new version entry in the catalog (single-writer assumptions; full concurrency control comes later).
- Introduce a `dataset-read` capability that:
  - Reads the latest or a specific version of a dataset by consulting the catalog.
  - Constructs a PyArrow-compatible dataset or table using all files for that version (no statistics-based pruning yet).
  - Provides a clean, Pythonic API surface for caller code.
- Keep storage to the local filesystem or simple URIs for now; richer multi-backend storage and file naming are handled in a later change.

## Impact

- Affected specs:
  - `dataset-write` (new)
  - `dataset-read` (new)
- Builds on existing specs:
  - `dataset-core` (dataset identity and URI resolution)
  - `catalog-store` (catalog tables and basic version tracking)
- Affected code (future implementation):
  - Public client API functions (e.g., `data_lagoon.write_dataset`, `data_lagoon.read_dataset`).
  - Internal helpers for normalizing inputs to Arrow and interacting with the catalog.

