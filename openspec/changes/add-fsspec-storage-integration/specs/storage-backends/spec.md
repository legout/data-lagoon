## MODIFIED Requirements

### Requirement: Dataset APIs Must Use Filesystem Abstraction
`write_dataset` and `read_dataset` SHALL use a filesystem abstraction (e.g., `fsspec`) to resolve dataset `base_uri` values, rather than assuming local paths.

#### Scenario: Write dataset to S3 using filesystem abstraction
- **WHEN** a dataset has `base_uri = 's3://example-bucket/sales'`
- **THEN** `write_dataset` SHALL obtain an `s3fs` filesystem via the storage abstraction
- **AND** it SHALL call `ds.write_dataset(..., filesystem=fs)` so files are written to S3
- **AND** the catalog SHALL record normalized S3 URIs for the written files.

### Requirement: Filesystem Info Stored with Catalog Entries
The catalog SHALL store file paths/URIs that include enough information for `read_dataset` to reinstantiate the correct filesystem (scheme + path).

#### Scenario: Read dataset from Azure storage
- **WHEN** a dataset’s files are stored under `abfs://container/path/...`
- **THEN** the catalog entries SHALL include URIs with the `abfs://` scheme
- **AND** `read_dataset` SHALL use the storage abstraction to open an Azure-compatible filesystem before constructing the dataset.
