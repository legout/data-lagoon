## Context
- Extends basic writes to support multiple storage backends (local, S3, GCS, Azure) via `fsspec`.
- Introduces UUID v7 file naming and explicit tombstone behavior.
- Builds on `add-basic-write-and-read-apis` and prepares for statistics/pruning changes.

## Goals
- Provide a storage abstraction that maps dataset `base_uri` → filesystem handle.
- Support at least: local filesystem, S3, GCS, Azure (using `fsspec` URLs).
- Enforce UUID v7 file naming so files are unique and time-sortable.
- Ensure catalog references only committed files; unreferenced files become tombstones.

## Non-Goals
- Implementing tombstone vacuum (handled in `add-vacuum-and-recovery-operations`).
- Handling complex partition layouts (basic partition support only).
- Advanced concurrency semantics (handled later).

## Design Overview

### Storage Abstraction
- Wrapper module `storage.py` that:
  - Parses `base_uri` and selects appropriate `fsspec` filesystem.
  - Provides helpers: `open_writer(path)`, `exists(path)`, `list_files(prefix)`, etc.
  - Caches filesystem instances per scheme for performance.

### File Naming
- Add helper `generate_parquet_filename()` returning `part-{uuidv7}.parquet`.
- For partitioned datasets, final path: `<base_uri>/<partition_dirs>/<filename>`.
- No temporary directories; rely on catalog to control visibility.

### Write Flow Changes
- `write_dataset` obtains filesystem via storage abstraction.
- Writes Parquet to a temp buffer/file (e.g., local temp) then uploads via filesystem.
- Records absolute path/URI in catalog.
- Tombstones: unreferenced files remain in storage until vacuum.

### Read Flow
- When reading, storage abstraction lists files or uses catalog entries with full paths.
- Works uniformly across local/remote backends.

## Key Decisions
- Use `fsspec` as the portable FS layer; default to `LocalFileSystem` when scheme absent.
- UUID v7 via `uuid7` library or custom generator (fallback to `uuid.uuid4` if needed).
- Keep per-file writes simple; later changes can add multi-file partitioned writes.

## Risks / Mitigations
- External dependencies (`fsspec`, cloud auth) increase setup complexity → document optional extras.
- Latency for remote writes → allow streaming from in-memory buffers.
- Missing UUID v7 support in stdlib → include lightweight helper implementing draft spec.

## Open Questions
- Should `base_uri` include dataset-specific subdirectories automatically?
- How to configure credentials for different clouds (env vars vs config objects)?
