## 1. Implementation

- [x] 1.1 Introduce storage abstraction that maps dataset URIs to `fsspec` filesystem + path (support local, S3, GCS, Azure).
- [x] 1.2 Update `write_dataset` to call `ds.write_dataset(..., filesystem=fs)` and construct per-version subdirectories via filesystem APIs.
- [x] 1.3 Update `read_dataset` to create datasets using `ds.dataset(file_paths, format='parquet', filesystem=fs)` for remote paths.
- [x] 1.4 Persist normalized file paths/URIs in catalog so readers know which filesystem to use.
- [ ] 1.5 Add tests using `fsspec`’s in-memory/filesystem mocks to ensure remote paths work.
- [ ] 1.6 Document configuration (credentials, dependencies) for remote backends.
