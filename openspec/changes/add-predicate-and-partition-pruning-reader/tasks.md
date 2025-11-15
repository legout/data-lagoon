## 1. Implementation

- [ ] 1.1 Extend `read_dataset` signature to accept predicates in a structured form
- [ ] 1.2 Implement catalog queries that use row-group statistics for pruning
- [ ] 1.3 Implement partition-based pruning using the `partitions` table
- [ ] 1.4 Build PyArrow `ParquetFragment`s and `FileSystemDataset` from pruned file/row-group lists
- [ ] 1.5 Ensure correct fallback behavior when statistics are missing or incomplete
- [ ] 1.6 Add tests and benchmarks showing reduced I/O vs baseline full scans

