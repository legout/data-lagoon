## ADDED Requirements

### Requirement: Core Type System
The system SHALL provide unified type definitions for table metadata and operations across all supported formats.

#### Scenario: Table metadata representation
- **WHEN** a table is retrieved from Unity Catalog
- **THEN** the system SHALL create a `TableMetadata` dataclass containing full_name, data_source_format, storage_location, and optional schema_json
- **AND** the format SHALL be one of "DELTA", "ICEBERG", or "PARQUET"

#### Scenario: Unified table interface
- **WHEN** a user interacts with any table format
- **THEN** the system SHALL provide a `BaseTable` class with consistent `to_arrow()` and `to_polars()` methods
- **AND** these methods SHALL return appropriate data types regardless of underlying format

### Requirement: UC Client Integration
The system SHALL provide a unified client interface for Unity Catalog operations using the official unitycatalog-python SDK.

#### Scenario: Table retrieval
- **WHEN** calling `get_table("catalog.schema.table")`
- **THEN** the client SHALL return table metadata from Unity Catalog
- **AND** SHALL translate UnityCatalog exceptions to structured Lagoon errors

#### Scenario: Table listing
- **WHEN** calling `list_tables("catalog", "schema")`
- **THEN** the client SHALL return a list of table metadata objects
- **AND** SHALL handle pagination if required by the API

#### Scenario: Table lifecycle management
- **WHEN** calling `create_table()` or `drop_table()`
- **THEN** the client SHALL execute the operation via unitycatalog-python
- **AND** SHALL provide clear error messages for failures

### Requirement: Table Adapter Protocol
The system SHALL define a protocol for format-specific table operations ensuring consistent behavior across all adapters.

#### Scenario: Standard adapter interface
- **WHEN** implementing a format adapter
- **THEN** it SHALL implement the `TableAdapter` protocol
- **AND** SHALL provide `to_arrow()`, `to_polars()`, `write()`, and `delete()` methods
- **AND** SHALL use consistent signatures across all formats

#### Scenario: Adapter compliance
- **WHEN** a new adapter is created
- **THEN** it SHALL pass protocol compliance tests
- **AND** SHALL handle format-specific operations transparently

### Requirement: Format Routing
The system SHALL automatically route table operations to the appropriate format adapter based on Unity Catalog metadata.

#### Scenario: Format detection
- **WHEN** a table operation is requested
- **THEN** the dispatcher SHALL inspect the `data_source_format` from Unity Catalog
- **AND** SHALL route to the corresponding adapter (Delta, Iceberg, or Parquet)

#### Scenario: Unsupported format handling
- **WHEN** an unknown format is encountered
- **THEN** the system SHALL raise `UnsupportedFormatError`
- **AND** SHALL provide clear guidance on supported formats

### Requirement: Testing Infrastructure
The system SHALL provide comprehensive testing infrastructure for all core components.

#### Scenario: UC client mocking
- **WHEN** testing UC client operations
- **THEN** tests SHALL use `respx` to mock HTTP responses
- **AND** SHALL simulate various success and error scenarios

#### Scenario: Routing tests
- **WHEN** testing the dispatcher
- **THEN** tests SHALL cover all supported format combinations
- **AND** SHALL verify proper adapter selection and error handling

#### Scenario: Type validation
- **WHEN** running type checking
- **THEN** mypy SHALL pass without errors
- **AND** all public APIs SHALL have complete type annotations
