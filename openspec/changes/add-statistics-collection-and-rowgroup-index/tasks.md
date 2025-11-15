## 1. Implementation

- [ ] 1.1 Implement statistics collection for DuckDB writes using `RETURN_STATS`
- [ ] 1.2 Implement statistics collection for PyArrow writes using `file_visitor` and `FileMetaData`
- [ ] 1.3 Populate `files` table with file-level metrics (size, row_count)
- [ ] 1.4 Populate `row_groups` table with row-group and per-column statistics
- [ ] 1.5 Populate `partitions` table with partition key/value pairs for each file
- [ ] 1.6 Add tests verifying statistics are correctly captured and stored

