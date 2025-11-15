## MODIFIED Requirements

### Requirement: Persist Row-Group Statistics From PyArrow Metadata
Every file produced by `write_dataset` SHALL persist the row-group statistics made available through `pyarrow.parquet.FileMetaData` directly into the catalog’s `row_groups` table.

#### Scenario: Capture row-group stats for PyArrow write
- **WHEN** `write_dataset` uses PyArrow’s dataset writer (with file visitor)
- **THEN** the visitor SHALL read each `RowGroupMetaData` entry and store `min`, `max`, and `null_count` per column as JSON
- **AND** those stats SHALL be available for pruning without re-opening the Parquet files.

### Requirement: Store Schema Version and Partition Data Per File
The metadata captured from `WrittenFile.metadata` SHALL be used to associate each file with a schema version and with the partition values encoded in the file path/partition spec.

#### Scenario: Write new schema version with partitions
- **WHEN** an incoming write adds a column (creating a new schema version) and writes to partition directories (e.g., `date=.../region=...`)
- **THEN** the file visitor SHALL record the Arrow schema bytes and partition key/value pairs
- **AND** the catalog SHALL insert a new `schema_versions` entry (if needed), link the file to that version, and store the partition key/value pairs in the `partitions` table.
