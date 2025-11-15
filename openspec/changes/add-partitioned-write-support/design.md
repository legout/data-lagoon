## Context
- Storage integration is in place; now we need to leverage PyArrow’s partitioning support so data can be written under `key=value/` directories.
- Partition metadata is required for partition pruning; capturing it at write time prevents expensive path parsing later.

## Goals
- Expose a `partition_by` parameter (list of column names or PyArrow partitioning objects) in `write_dataset`.
- Use `ds.write_dataset(..., partitioning=ds.partitioning(flavor="hive", field_names=...))` to create Hive-style directories across all filesystems.
- Capture partition key/value pairs for each file and persist them in the catalog’s `partitions` table.
- Maintain compatibility with existing per-version layout (e.g., `<base>/v1/date=.../region=.../part-...parquet`).

## Design

### Partition Configuration
- Accept `partition_by: Sequence[str] | None` parameter; default `None`.
- Validate that specified columns exist in the incoming schema.
- Create PyArrow partitioning: `partitioning = ds.partitioning(field_names=partition_by, flavor="hive")`.
- Pass `partitioning=partitioning` to `ds.write_dataset`.

### Directory Layout
- Reuse per-version directory root (e.g., `<root>/v{version}`).
- PyArrow will create subdirectories like `date=.../region=...` under that root automatically.

### Metadata Capture
- File visitor receives `WrittenFile.metadata` and `written.path` relative to base_dir (includes partition directories). Parse partition key/value pairs from the path segments (split by `/`, keep segments containing `=`).
- Persist partition entries via catalog helper (one row per key/value per file).

### Catalog / API Changes
- `WriteResult` can expose partition info per file (optional).
- Update spec to state that partition metadata is always stored and available for partition pruning.

## Risks
- Large numbers of partitions might create many directories; rely on PyArrow’s writer to manage concurrency.
- Users may pass unsupported partition expressions; initial implementation supports simple column names (Hive flavor). Document limitations.
