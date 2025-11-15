## ADDED Requirements

### Requirement: Write Dataset From Arrow-Like Inputs
The system SHALL provide a `write_dataset` API that accepts Arrow `Table`, Arrow `RecordBatchReader`, Pandas DataFrame, or Polars DataFrame and writes the data to the dataset’s storage as Parquet files.

#### Scenario: Append Pandas DataFrame to dataset
- **WHEN** a client calls `write_dataset` with a Pandas DataFrame and a dataset reference (name or URI)
- **THEN** the system SHALL normalize the input to an Arrow representation
- **AND** it SHALL write one or more Parquet files under the dataset’s `base_uri`
- **AND** it SHALL return a result object indicating the dataset identifier and the number of rows written.

#### Scenario: Reject unsupported input type
- **WHEN** a client calls `write_dataset` with an unsupported data type
- **THEN** the system SHALL raise a clear error indicating the accepted input types.

### Requirement: Write Operation Records Basic Metadata
For each successful `write_dataset` call, the system SHALL record a new version for the dataset in the catalog and persist basic file metadata.

#### Scenario: Record transaction and files after write
- **WHEN** `write_dataset` successfully writes Parquet files for a dataset
- **THEN** the system SHALL insert a new row into the `transactions` table with the dataset identifier, a monotonically increasing `version`, a timestamp, and an `operation` value such as `"append"`
- **AND** it SHALL insert one row into the `files` table for each created Parquet file, including at least `file_path`, `file_size_bytes`, `row_count`, and `created_at`
- **AND** it SHALL update the dataset’s `current_version` field to the new version.

### Requirement: Catalog-Level Atomicity for Single Writer
In a single-writer context, the system SHALL ensure that catalog updates for a `write_dataset` call are atomic: either all metadata changes for the write are committed, or none are.

#### Scenario: Partial failure rolls back catalog state
- **WHEN** a failure occurs after some Parquet files are written but before catalog updates are committed
- **THEN** the system SHALL roll back the catalog transaction so that no new version appears in the catalog
- **AND** any files written during the failed operation SHALL NOT be referenced by the catalog (they may be treated as tombstones by later maintenance changes).

