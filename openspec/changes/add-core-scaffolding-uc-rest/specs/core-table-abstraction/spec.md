## ADDED Requirements

### Requirement: Table Metadata Structure
The system SHALL provide a `TableMetadata` dataclass that captures essential table information from Unity Catalog.

#### Scenario: Create table metadata from UC response
- **WHEN** Unity Catalog returns table information
- **THEN** the system SHALL create a `TableMetadata` instance with full_name, data_source_format, and storage_location
- **AND** the data_source_format SHALL be one of: "DELTA", "ICEBERG", "PARQUET"
- **AND** the storage_location SHALL be a valid URI string

#### Scenario: Handle optional schema information
- **WHEN** Unity Catalog provides schema information
- **THEN** the TableMetadata SHALL include schema_json as an optional dictionary field
- **WHEN** schema information is not available
- **THEN** schema_json SHALL default to None

### Requirement: Base Table Facade
The system SHALL provide a `BaseTable` class that serves as the primary interface for table operations.

#### Scenario: Create BaseTable from metadata
- **WHEN** creating a table instance
- **THEN** BaseTable SHALL accept a TableMetadata instance
- **AND** SHALL expose the metadata through a read-only property
- **AND** SHALL initialize adapter-specific state

#### Scenario: Convert table to Arrow format
- **WHEN** a user calls to_arrow() on a BaseTable instance
- **THEN** the method SHALL return a pyarrow.Table
- **AND** SHALL delegate to the appropriate format adapter
- **AND** SHALL raise FormatError if conversion is not supported

#### Scenario: Convert table to Polars format
- **WHEN** a user calls to_polars() on a BaseTable instance
- **THEN** the method SHALL return a polars.DataFrame
- **AND** SHALL use Arrow conversion internally when possible
- **AND** SHALL raise FormatError if conversion is not supported

#### Scenario: Write data to table
- **WHEN** a user calls write() with data and mode
- **THEN** the method SHALL delegate to the appropriate format adapter
- **AND** SHALL accept Arrow table, Polars DataFrame, or pandas DataFrame
- **AND** SHALL support mode="append" and mode="overwrite"
- **AND** SHALL raise WriteError if the operation fails

#### Scenario: Delete data from table
- **WHEN** a user calls delete() with optional where clause
- **THEN** the method SHALL delegate to the appropriate format adapter
- **AND** SHALL accept None for full table deletion or string for conditional deletion
- **AND** SHALL raise NotImplementedError if the format doesn't support deletion
- **AND** SHALL raise DeleteError if the operation fails

### Requirement: Type Safety
The system SHALL ensure all core abstractions are fully typed for static analysis.

#### Scenario: Type checking compliance
- **WHEN** running mypy on the core module
- **THEN** all functions SHALL have complete type annotations
- **AND** all dataclass fields SHALL have explicit types
- **AND** mypy SHALL report no type errors

#### Scenario: Runtime type validation
- **WHEN** creating TableMetadata with invalid types
- **THEN** the system SHALL raise TypeError immediately
- **AND** provide clear error messages about the expected types