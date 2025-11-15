## ADDED Requirements

### Requirement: Read Latest Dataset Version
The system SHALL provide a `read_dataset` API that returns the latest committed version of a dataset as a PyArrow-compatible dataset or table.

#### Scenario: Read latest version by name
- **WHEN** a client calls `read_dataset` with a dataset `name` and no explicit `version`
- **THEN** the system SHALL resolve the dataset via the catalog
- **AND** it SHALL look up the dataset’s `current_version`
- **AND** it SHALL load all Parquet files associated with that version from the dataset’s `base_uri`
- **AND** it SHALL return the data as a PyArrow-compatible dataset or table.

### Requirement: Read Specific Dataset Version
The system SHALL allow callers to read a specific historical version of a dataset.

#### Scenario: Read previous dataset version
- **WHEN** a client calls `read_dataset` with a dataset reference and an explicit `version` value
- **THEN** the system SHALL load only the files associated with that version from the catalog
- **AND** it SHALL return the corresponding data as a PyArrow-compatible dataset or table
- **AND** it SHALL NOT include files from other versions.

### Requirement: No Catalog-Based Pruning in Basic Reads
In this basic capability, `read_dataset` SHALL include all files belonging to the selected version and SHALL NOT rely on catalog statistics for file or row-group pruning; filtering MAY still be applied by downstream compute engines.

#### Scenario: Read with filter but no pruning
- **WHEN** a client calls `read_dataset` and then applies a filter using a downstream engine (e.g., DuckDB, Polars, or PyArrow)
- **THEN** the system SHALL first construct the dataset using all files for the selected version
- **AND** it SHALL NOT attempt to prune files or row groups based on stored statistics as part of this capability.

