## ADDED Requirements
### Requirement: Format-Aware Dispatch
The system SHALL provide a dispatcher that automatically routes table operations to the appropriate adapter based on the table's format type, ensuring seamless format abstraction for users.

#### Scenario: Route Delta table operations
- **WHEN** build_table is called with DELTA format metadata
- **THEN** dispatcher SHALL create DeltaAdapter instance
- **AND** adapter SHALL be configured with storage location
- **AND** returned table SHALL support Delta-specific operations

#### Scenario: Route Iceberg table operations
- **WHEN** build_table is called with ICEBERG format metadata
- **THEN** dispatcher SHALL create IcebergAdapter instance
- **AND** adapter SHALL be configured with full table name
- **AND** returned table SHALL support Iceberg-specific operations

#### Scenario: Route Parquet table operations
- **WHEN** build_table is called with PARQUET format metadata
- **THEN** dispatcher SHALL create ParquetAdapter instance
- **AND** adapter SHALL be configured with storage location
- **AND** returned table SHALL support Parquet-specific operations

### Requirement: Unsupported Format Handling
The system SHALL gracefully handle requests for unsupported table formats with clear error messages and format validation.

#### Scenario: Detect unsupported format
- **WHEN** build_table is called with unknown format
- **THEN** UnsupportedFormatError SHALL be raised
- **AND** error message SHALL list supported formats
- **AND** original format SHALL be included in error context

#### Scenario: Validate metadata completeness
- **WHEN** build_table receives incomplete metadata
- **THEN** ValidationError SHALL be raised
- **AND** error SHALL indicate missing required fields
- **AND** suggestions SHALL be provided for common issues

### Requirement: Adapter Selection Logic
The system SHALL implement intelligent routing logic that considers both format type and data characteristics to choose the most appropriate adapter for each operation.

#### Scenario: Choose optimal adapter based on format
- **WHEN** build analyzes table metadata
- **THEN** DELTA SHALL always route to DeltaAdapter
- **AND** ICEBERG SHALL always route to IcebergAdapter  
- **AND** PARQUET SHALL always route to ParquetAdapter
- **AND** routing SHALL be deterministic and predictable
