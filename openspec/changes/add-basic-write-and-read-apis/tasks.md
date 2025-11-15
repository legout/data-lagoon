## 1. Implementation

- [x] 1.1 Define public `write_dataset` API and input normalization to Arrow
- [x] 1.2 Implement basic Parquet writes to the dataset `base_uri` (local or simple URI)
- [x] 1.3 Record basic file metadata and new version entries in the catalog (single-writer)
- [x] 1.4 Define public `read_dataset` API that loads all files for a given version
- [x] 1.5 Return a PyArrow-compatible dataset or table from `read_dataset`
- [x] 1.6 Add unit tests covering basic write/read flows and error cases
