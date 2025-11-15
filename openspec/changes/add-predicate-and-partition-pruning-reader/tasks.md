## 1. Implementation

- [x] 1.1 Extend `read_dataset` signature to accept predicates in a structured form
- [x] 1.2 Implement catalog queries that use row-group statistics for pruning
- [x] 1.3 Implement partition-based pruning using the `partitions` table
- [x] 1.4 Build PyArrow `FileSystemDataset` from pruned file lists and materialize row groups when needed
- [x] 1.5 Ensure correct fallback behavior when statistics are missing or incomplete
- [x] 1.6 Add tests demonstrating reduced results and correctness vs baseline full scans
