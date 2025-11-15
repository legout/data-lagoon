## Context
- Implements the first public `write_dataset` / `read_dataset` APIs.
- Depends on `dataset-core`, `catalog-store`, and `structured-dataset-references`.
- Out of scope: pruning, transactions, schema evolution, multi-writer guarantees.

## Goals
- Normalize Arrow-compatible inputs (Arrow `Table`, `RecordBatchReader`, Polars, etc.) into a consistent representation.
- Write Parquet files under the dataset’s `base_uri`, assuming a single local path for now.
- Record minimal metadata in the catalog (dataset identity + stub version entry if needed).
- Read the latest version by loading all files for that version (no pruning statistics yet).
- Return PyArrow-compatible dataset/table objects suitable for future engine helpers.

## Non-Goals
- Collecting detailed file/row-group stats (handled in later changes).
- Handling multiple partitions or remote storage backends (later change).
- Full transaction semantics or concurrent writes (later change).
- Schema evolution/type promotion (later change).

## API Surface

```python
from data_lagoon import DatasetRef
from data_lagoon.dataset import write_dataset, read_dataset, DatasetError, WriteResult

result = write_dataset(
    DatasetRef(name="sales", base_uri="file:///tmp/sales.parquet"),
    data=table_or_df,
    catalog_uri="sqlite:///catalog.db",
)

table = read_dataset(
    DatasetRef(name="sales"),
    catalog_uri="sqlite:///catalog.db",
    version=None,  # defaults to latest
)
```

### Input normalization
- Accept: Arrow `Table`, `RecordBatch`, `RecordBatchReader`, Pandas DataFrame, Polars DataFrame.
- Convert to Arrow `Table` before writing.
- Raise `DatasetError` for unsupported types.

### Writes
- Resolve dataset via catalog (`DatasetRef` or legacy string).
- Require `base_uri` (local filesystem path for now).
- Write a single Parquet file (later changes introduce partitioning + storage layers).
- Return `WriteResult` with dataset ref, row count, and list of file paths.
- Record basic catalog metadata (dataset exists, version increments optional for now).

### Reads
- Resolve dataset via catalog.
- Load all files for the latest version (basic change: single file, no stats).
- Return Arrow `Table` or `Dataset` (for now, table is sufficient).
- Provide hooks for future `version` parameter (time travel).

## Key Decisions
- Use PyArrow’s `pq.write_table`/`pq.read_table` for simplicity.
- Keep catalog interaction minimal: ensure dataset exists, but postpone detailed transaction/version handling until a later change.
- `WriteResult` is intentionally simple (row count + files) so later changes can add stats/versions without breaking API.

## Risks / Trade-offs
- Single-file writes become inefficient for large datasets; mitigated in later changes (storage layer, partitioning).
- Catalog metadata is minimal; future changes must retrofit version IDs without breaking current data (plan to treat these writes as version 1).
- Without transactions, concurrent writers may clobber each other; callers must serialize writes until `add-transactions-and-concurrency-control`.

## Open Questions
- Where to persist version numbers now? (Option: stub entry in `transactions`; or defer until concurrency change.)
- How to surface write options (partitioning, compression) before storage layer change? (Probably keep API simple now and add optional kwargs later.)
