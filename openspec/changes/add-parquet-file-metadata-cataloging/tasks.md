## 1. Implementation

- [x] 1.1 Extend the dataset `file_visitor` to extract `pyarrow.parquet.FileMetaData` for each file (row-group stats, schema).
- [x] 1.2 Update catalog write helpers to accept schema IDs, row-group stats, and partition key/value pairs.
- [x] 1.3 Persist schema versions (creating new `schema_versions` rows as needed) and link files to the correct schema version.
- [x] 1.4 Persist row-group statistics (`stats_min_json`, `stats_max_json`, `null_counts_json`) and partition metadata for each file.
- [x] 1.5 Expose captured metadata in `WriteResult` (or logging) for debugging purposes.
- [x] 1.6 Add unit/integration tests verifying metadata is stored and retrievable from the catalog.
