## ADDED Requirements

### Requirement: DuckDB Integration Helper
The system SHALL provide a helper that constructs a DuckDB relation or equivalent object from a dataset, leveraging pruning-aware file and row-group selection.

#### Scenario: Create DuckDB relation from dataset
- **WHEN** a client has obtained a dataset handle or version reference
- **AND** they call the DuckDB integration helper with optional predicates and projection
- **THEN** the system SHALL use the existing pruning logic to determine the set of files and row groups to read
- **AND** it SHALL construct a DuckDB relation (e.g., via `relation_from_arrow_dataset` or a `read_parquet` call) over those files
- **AND** the resulting relation SHALL respect the same snapshot and pruning semantics as `read_dataset`.

### Requirement: Polars Integration Helper
The system SHALL provide a helper that constructs a Polars `LazyFrame` (or equivalent lazy query object) from a dataset using pruning-aware file selection.

#### Scenario: Create Polars lazy scan from dataset
- **WHEN** a client calls the Polars integration helper for a dataset with optional predicates and projection
- **THEN** the system SHALL determine the set of files and row groups to read using catalog-based pruning
- **AND** it SHALL construct a Polars `LazyFrame` via `scan_pyarrow_dataset` or `scan_parquet` over those files
- **AND** downstream Polars operations SHALL benefit from both the library’s pruning and Polars’ own pushdown.

### Requirement: DataFusion Integration Helper
The system SHALL provide a helper that constructs a DataFusion dataset or table registration from the pruned file list and schema.

#### Scenario: Register dataset in DataFusion
- **WHEN** a client uses the DataFusion integration helper with a dataset and optional predicates
- **THEN** the system SHALL compute the candidate file list using catalog pruning
- **AND** it SHALL register or read those files via a `SessionContext` (e.g., `read_parquet_glob`)
- **AND** the resulting DataFusion table SHALL support predicate pushdown using row-group statistics.

### Requirement: Shared Pruning Logic Across Integrations
Engine-specific helpers SHALL reuse the same catalog-based pruning logic as `read_dataset` so that file and row-group selection behavior is consistent.

#### Scenario: Consistent file selection across engines
- **WHEN** the same dataset, version, and predicate are used with `read_dataset`, the DuckDB helper, and the Polars helper
- **THEN** the underlying set of files and row groups selected for reading SHALL be the same across all three
- **AND** any differences in observed behavior SHALL only arise from the engines’ own query planners, not from mismatched file selection.

