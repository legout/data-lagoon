## Context
- `write_dataset` already uses PyArrow’s Dataset API with a `file_visitor`, but we only persist path/size/row count.
- `WrittenFile.metadata` exposes `pyarrow.parquet.FileMetaData`, containing the row-group information we need for pruning, schema tracking, and partition metadata.
- Capturing this metadata at write time keeps the catalog authoritative and avoids re-reading Parquet files during reads.

## Goals
- Extract complete metadata from each `WrittenFile`:
  - Row-group counts and sizes.
  - Column statistics (min, max, null count).
  - Schema fingerprint (Arrow schema bytes).
  - Partition values derived from directory structure or writer input.
- Persist metadata in catalog tables via a single helper to keep commits atomic.
- Provide optional access to the metadata (e.g., via `WriteResult.metadata`) for observability.

## Design

### Metadata Extraction
```python
@dataclass
class RowGroupMetadata:
    index: int
    row_count: int
    stats_min_json: str
    stats_max_json: str
    null_counts_json: str

@dataclass
class FileMetadata:
    path: str
    row_count: int
    file_size_bytes: int
    schema: pa.Schema
    parquet_metadata: dict[str, Any]  # from `FileMetaData.to_dict()`
    row_groups: list[RowGroupMetadata]
    partitions: dict[str, str]
```
- Use `written.metadata.to_dict()` to capture the full Parquet metadata; store the dict (or selected subsets) alongside derived row-group stats.
- `WrittenFile.metadata.schema` gives the Arrow schema.
- Iterate over row groups/columns (from either the dict or the native metadata objects) to build JSON blobs for stats.
- Partition values inferred from `written.path` segments or PyArrow’s partition descriptors (if provided).

### Catalog Persistence
- Introduce `catalog.record_file_metadata(dataset, version, file_metadatas)`:
  1. Ensure schema version exists (serialize schema via `pa.ipc.serialize_schema`).
  2. Insert file rows with schema version reference and `stats_complete` flag.
  3. Insert row-group rows referencing file IDs.
  4. Insert partition rows referencing file IDs.
- Wrap in a database transaction alongside the existing `transactions` insert.

### API/Surface Changes
- `WriteResult` gains an optional `metadata` field (list of `FileMetadata` or simplified dict).
- Document that `read_dataset` can rely on catalog stats without re-opening Parquet files.

## Risks / Mitigations
- Metadata volume: row-group stats can be large; store JSON as text but consider compression later.
- Missing stats: PyArrow may omit stats for some columns; store `null` entries to signal incomplete data.
- Partition parsing on remote filesystems: rely on the normalized paths we already store (fsspec’s `unstrip_protocol`).

## Open Questions
- Should we deduplicate schema versions globally or per dataset? (Initial approach: per dataset.)
- Do we need to store column-level encodings/compression? (Out of scope for now.)
