## ADDED Requirements
### Requirement: Table Metadata Representation
The system SHALL provide a standardized data structure to represent Unity Catalog table metadata including format, location, and schema information.

#### Scenario: Create TableMetadata from UC response
- **WHEN** UC client returns table metadata
- **THEN** TableMetadata SHALL be instantiated with full_name, data_source_format, storage_location
- **AND** schema_json SHALL be populated when available
- **AND** all fields SHALL be properly typed

#### Scenario: Validate required metadata fields
- **WHEN** TableMetadata is created without required fields
- **THEN** validation SHALL raise appropriate TypeError
- **AND** error message SHALL indicate missing required fields

### Requirement: Unified Table Interface
The system SHALL provide a base table interface that abstracts format-specific operations while maintaining consistent method signatures across all table formats.

#### Scenario: Convert table to Arrow format
- **WHEN** BaseTable.to_arrow() is called on any table
- **THEN** method SHALL return pyarrow.Table
- **AND** result SHALL be format-agnostic
- **AND** data SHALL preserve original schema and content

#### Scenario: Convert table to Polars format
- **WHEN** BaseTable.to_polars() is called on any table
- **THEN** method SHALL return polars.DataFrame
- **AND** conversion SHALL be efficient via Arrow intermediate
- **AND** result SHALL maintain data types accurately

#### Scenario: Write data to table
- **WHEN** BaseTable.write() is called with mode="append"
- **THEN** data SHALL be appended to existing table
- **AND** operation SHALL respect format-specific semantics
- **AND** appropriate errors SHALL be raised for unsupported operations

#### Scenario: Delete table data
- **WHEN** BaseTable.delete() is called with WHERE clause
- **THEN** data matching predicate SHALL be deleted
- **AND** operation SHALL follow format-specific capabilities
- **AND** unsupported operations SHALL raise NotImplementedError
