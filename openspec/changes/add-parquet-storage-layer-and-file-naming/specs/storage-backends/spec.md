## ADDED Requirements

### Requirement: Support Multiple Storage Backends
The system SHALL support reading and writing datasets on multiple storage backends using dataset `base_uri` values, including at least:
- Local files (e.g., `/data/lake/sales` or `file:///data/lake/sales`).
- AWS S3 (e.g., `s3://bucket/path`).
- Google Cloud Storage (e.g., `gs://bucket/path`).
- Azure Data Lake / Blob Storage (e.g., `abfs://container/path` or equivalent).

#### Scenario: Write dataset to local filesystem
- **WHEN** a dataset is registered with a `base_uri` pointing to a local path
- **AND** a client writes data to that dataset
- **THEN** the system SHALL write Parquet files under that local path
- **AND** it SHALL register the resulting file paths in the catalog.

#### Scenario: Write dataset to S3
- **WHEN** a dataset is registered with a `base_uri` such as `s3://bucket/path`
- **AND** a client writes data to that dataset
- **THEN** the system SHALL use the storage abstraction to write Parquet files to S3 under that prefix
- **AND** it SHALL register the resulting S3 object keys as `file_path` values in the catalog.

### Requirement: Use a Unified Filesystem Abstraction
The system SHALL use a unified filesystem abstraction (such as `fsspec`) to interact with different storage backends so that higher-level components do not depend on backend-specific APIs.

#### Scenario: Open dataset path via filesystem abstraction
- **WHEN** the system needs to list, read, or write Parquet files for a dataset
- **THEN** it SHALL obtain a filesystem object based on the dataset’s `base_uri` scheme
- **AND** it SHALL perform file operations (create, list, delete) using that abstraction rather than backend-specific clients.

### Requirement: Stable Path Construction Under base_uri
The system SHALL construct file paths for dataset contents by joining the dataset’s `base_uri` with partition directories and file names in a consistent manner.

#### Scenario: Construct file path for partitioned dataset
- **WHEN** a dataset is partitioned by one or more columns (e.g., `date=2024-01-01`)
- **AND** files are written for that partition
- **THEN** the system SHALL create paths of the form `<base_uri>/<partition_dirs>/<filename>`
- **AND** these paths SHALL be recorded exactly in the catalog’s `file_path` column.

