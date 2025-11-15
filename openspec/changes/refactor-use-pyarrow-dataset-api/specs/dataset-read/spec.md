## MODIFIED Requirements

### Requirement: Construct Arrow Dataset Objects for Reads
`read_dataset` SHALL construct a PyArrow Dataset (`pyarrow.dataset.Dataset` or `FileSystemDataset`) from the catalog’s file list before materializing results.

#### Scenario: Read dataset as Arrow Dataset
- **WHEN** a client calls `read_dataset`
- **THEN** the system SHALL gather file paths for the requested version from the catalog
- **AND** it SHALL call `pyarrow.dataset.dataset` (or equivalent) to build a dataset object representing those files
- **AND** it MAY materialize the dataset to a `pa.Table` for convenience, but the dataset abstraction SHALL be the primary representation for downstream integrations.

### Requirement: Support Dataset Handle Return
`read_dataset` SHALL offer a way to return the Dataset handle directly (or expose it via helper methods) so that engine integrations can consume it without re-parsing Parquet files.

#### Scenario: Client requests dataset handle
- **WHEN** a client opts to receive the dataset object (e.g., via `as_dataset=True`)
- **THEN** the system SHALL return the constructed PyArrow Dataset
- **AND** downstream helpers (DuckDB, Polars, etc.) SHALL be able to reuse it without additional file discovery.
