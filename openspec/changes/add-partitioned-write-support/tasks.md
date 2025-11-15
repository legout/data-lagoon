## 1. Implementation

- [x] 1.1 Add a `partition_by` parameter (and/or dataset-level configuration) to `write_dataset`.
- [x] 1.2 Pass partition information to `ds.write_dataset` so files land in Hive-style partition directories.
- [x] 1.3 Update the file visitor to capture partition key/value pairs from the writer (or path segments) and persist them via the catalog helper.
- [x] 1.4 Ensure versioned directory layout still works with partition subdirectories and remote filesystems.
- [x] 1.5 Add tests verifying partitioned writes create expected directory structures and catalog partition entries.
