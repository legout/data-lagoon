## MODIFIED Requirements

### Requirement: Capture Row-Group Statistics During Every Write
Every `write_dataset` call SHALL capture row-group statistics (when available from the engine) and persist them in the catalog immediately, rather than deferring to a later change.

#### Scenario: PyArrow write captures row-group stats
- **WHEN** `write_dataset` uses PyArrow’s dataset writer
- **THEN** the file visitor SHALL iterate `WrittenFile.metadata.row_groups`
- **AND** it SHALL store `min`, `max`, and `null_count` per column in the `row_groups` table.

### Requirement: Record Partition Metadata at Write Time
When datasets are partitioned (e.g., via directory structure), partition key/value pairs SHALL be extracted during the write and persisted in the `partitions` table.

#### Scenario: Partitioned write records partition values
- **WHEN** a dataset is written with partition subdirectories like `date=2024-01-01/region=us`
- **THEN** the write logic SHALL parse these segments and insert `key=value` pairs into the catalog.
