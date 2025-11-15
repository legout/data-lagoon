## Context
- After moving to PyArrow’s Dataset API, we now have access to rich metadata for each file via `WrittenFile.metadata`. Currently we only store file path/size/row count, leaving downstream features (pruning, schema evolution) without the data they need unless we re-read Parquet footers later.
- Capturing and persisting metadata during the write keeps the catalog authoritative and avoids expensive reprocessing.

## Goals
- Extract row-group statistics (`min`, `max`, `null_count`) per column from `WrittenFile.metadata`.
- Capture partition key/value pairs derived from directory structure or writer partition expressions.
- Associate each file with a schema version (storing Arrow schema serialization if it changes).
- Persist metadata to catalog tables (`files`, `row_groups`, `partitions`, `schema_versions`) via a reusable helper.

## Design Overview

### Metadata Extraction
- Extend file visitor to build a `FileMetadata` structure:
  ```python
  @dataclass
  class FileMetadata:
      path: str
      row_count: int
      file_size_bytes: int
      schema: pa.Schema
      partitions: dict[str, str]
      row_groups: list[RowGroupMetadata]
  ```
- `RowGroupMetadata` stores `index`, `row_count`, `stats_min_json`, `stats_max_json`, `null_counts_json`.
- Partition values parsed from file path segments (e.g., `date=.../region=...`).

### Catalog Persistence
- Replace `record_basic_write` with a richer helper (`record_write_with_metadata`) that:
  - Inserts/updates `schema_versions` when a new schema appears.
  - Inserts `files` rows with `schema_version_id`.
  - Inserts `row_groups` and `partitions` rows.
- Wrap operations in the existing transaction to maintain atomicity.

### API Surface
- `WriteResult` may expose `metadata` for debugging (optional).
- Provide helper functions to query metadata from the catalog for tests and future engine integrations.

## Risks / Mitigations
- Metadata volume could be large for many row groups → store JSON blobs compactly, consider compression or summarization later.
- Some writers may not produce stats (NULLs) → store `None` values and document fallback.
- Partition parsing might mis-handle unusual directory names → rely on PyArrow’s partitioning info when available.

## Relation to Existing Changes
- Complements `add-statistics-collection-and-rowgroup-index` by delivering the metadata earlier; that change can now focus on advanced scenarios (DuckDB stats, pruning).
