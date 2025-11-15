## 1. Implementation

- [ ] 1.1 Extend file visitor to extract row-group stats (min/max/null counts) from `WrittenFile.metadata`.
- [ ] 1.2 Parse partition key/value pairs from file paths and/or writer-provided partition expressions.
- [ ] 1.3 Serialize metadata into catalog tables (`files`, `row_groups`, `partitions`, `schema_versions`).
- [ ] 1.4 Update `WriteResult` / logging to expose captured metadata for debugging.
- [ ] 1.5 Add tests ensuring metadata is persisted and retrievable (e.g., catalog queries return expected stats).
