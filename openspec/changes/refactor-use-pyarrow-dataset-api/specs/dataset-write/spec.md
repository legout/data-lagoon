## MODIFIED Requirements

### Requirement: Use Arrow Dataset API for Writes
`write_dataset` SHALL use PyArrow’s Dataset writer (`pyarrow.dataset.write_dataset`) to emit Parquet outputs, even for basic single-partition datasets.

#### Scenario: Write dataset via dataset API
- **WHEN** a client writes data to a dataset
- **THEN** the implementation SHALL call `pyarrow.dataset.write_dataset` (or equivalent dataset abstraction) rather than `pyarrow.parquet.write_table`
- **AND** it SHALL use the dataset writer’s hooks (e.g., `file_visitor`) to collect file paths and metadata for catalog persistence.

### Requirement: Capture File Metadata via File Visitor
During writes, the system SHALL use the dataset writer’s callback mechanisms (e.g., `file_visitor`) to capture the path, row counts, and stats of each generated file for insertion into the catalog.

#### Scenario: Record file metadata from write
- **WHEN** `write_dataset` completes
- **THEN** it SHALL have collected file paths from the dataset writer’s callbacks
- **AND** those paths SHALL be the ones persisted in the `files` table for the new version.
