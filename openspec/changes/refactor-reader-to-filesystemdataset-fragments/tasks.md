## 1. Implementation

- [x] 1.1 Review existing `read_dataset` pruning implementation and identify all direct Parquet reads that must be removed.
- [x] 1.2 Introduce a predicate-to-Arrow-Expression adapter so `(column, op, value)` inputs can be converted into `pyarrow.dataset.Expression` objects.
- [x] 1.3 Implement a fragment builder that:
  - [x] 1.3.1 Resolves a `pyarrow.fs.FileSystem` rooted at the dataset base (similar to Delta’s use of `SubTreeFileSystem`).
  - [x] 1.3.2 For each pruned file, constructs a `ParquetFragment` with `row_groups` restricted to candidates.
  - [x] 1.3.3 Attaches a `partition_expression` encoding partition key/value filters and statistics-based constraints.
- [x] 1.4 Build a `FileSystemDataset` via `pyarrow.dataset.FileSystemDataset` and update `read_dataset` to always materialize via `dataset.to_table(filter=...)`.
- [x] 1.5 Ensure fallback behavior:
  - [x] 1.5.1 If statistics are missing, fragments still include all row groups but retain partition pruning.
  - [x] 1.5.2 If no predicates are provided, the dataset is built from all files/fragments without extra expressions.
- [x] 1.6 Add tests comparing:
  - [x] 1.6.1 Results from the new path vs. the previous “full scan + filter in-memory” behavior.
  - [x] 1.6.2 I/O characteristics (number of fragments/row groups touched) for selective vs. non-selective predicates (basic unit tests verifying selective filters return fewer rows).
