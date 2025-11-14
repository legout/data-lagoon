## ADDED Requirements

### Requirement: Format Detection Logic
The system SHALL provide a dispatcher that automatically detects table formats and routes operations to appropriate adapters.

#### Scenario: Detect Delta format
- **WHEN** Unity Catalog indicates data_source_format is "DELTA"
- **THEN** the dispatcher SHALL route operations to the DeltaAdapter
- **AND** SHALL pass the storage_location to the adapter
- **AND** SHALL validate that the location contains valid Delta table files

#### Scenario: Detect Iceberg format
- **WHEN** Unity Catalog indicates data_source_format is "ICEBERG"
- **THEN** the dispatcher SHALL route operations to the PyIcebergAdapter
- **AND** SHALL pass the full table name for Iceberg REST catalog access
- **AND** SHALL configure the adapter with the UC Iceberg REST endpoint

#### Scenario: Detect Parquet format
- **WHEN** Unity Catalog indicates data_source_format is "PARQUET"
- **THEN** the dispatcher SHALL route operations to the PyArrowAdapter
- **AND** SHALL pass the storage_location for the Parquet folder
- **AND** SHALL treat the table as an external table

### Requirement: Adapter Factory Function
The system SHALL provide a centralized function for creating table instances with appropriate adapters.

#### Scenario: Build table from Unity Catalog metadata
- **WHEN** calling build_table() with table metadata
- **THEN** the function SHALL create a BaseTable instance
- **AND** SHALL attach the correct format adapter based on data_source_format
- **AND** SHALL configure the adapter with the appropriate connection parameters
- **AND** SHALL return the configured BaseTable instance

#### Scenario: Handle unknown formats
- **WHEN** encountering an unsupported data_source_format
- **THEN** the dispatcher SHALL raise UnsupportedFormatError
- **AND** SHALL include the detected format in the error message
- **AND** SHALL list supported formats for user guidance

### Requirement: Format-Specific Configuration
The dispatcher SHALL handle format-specific adapter configuration requirements.

#### Scenario: Configure Delta adapter
- **WHEN** creating a DeltaAdapter instance
- **THEN** the dispatcher SHALL configure S3-compatible storage options
- **AND** SHALL set up proper endpoint and authentication parameters
- **AND** SHALL handle path-style addressing when required

#### Scenario: Configure Iceberg adapter
- **WHEN** creating a PyIcebergAdapter instance
- **THEN** the dispatcher SHALL configure the Iceberg REST catalog endpoint
- **AND** SHALL set up authentication tokens for UC access
- **AND** SHALL configure appropriate warehouse parameters

#### Scenario: Configure Parquet adapter
- **WHEN** creating a PyArrowAdapter instance
- **THEN** the dispatcher SHALL configure PyArrow filesystem for the storage location
- **AND** SHALL set up S3-compatible storage parameters
- **AND** SHALL handle partitioning information if available

### Requirement: Error Handling and Validation
The dispatcher SHALL validate inputs and handle errors appropriately.

#### Scenario: Validate table metadata
- **WHEN** receiving table metadata from Unity Catalog
- **THEN** the dispatcher SHALL validate required fields are present
- **AND** SHALL verify storage_location is a valid URI
- **AND** SHALL raise ValidationError if metadata is incomplete

#### Scenario: Handle adapter creation failures
- **WHEN** adapter instantiation fails
- **THEN** the dispatcher SHALL raise AdapterError
- **AND** SHALL include the original exception details
- **AND** SHALL provide troubleshooting guidance

#### Scenario: Handle storage access issues
- **WHEN** adapter cannot access the storage location
- **THEN** the dispatcher SHALL raise StorageError
- **AND** SHALL include connection details for debugging
- **AND** SHALL suggest configuration fixes

### Requirement: Dispatcher Extensibility
The dispatcher SHALL be designed to support new formats without breaking existing functionality.

#### Scenario: Register new adapter
- **WHEN** adding support for a new table format
- **THEN** the dispatcher SHALL support adapter registration
- **AND** SHALL not require modification of existing routing logic
- **AND** SHALL maintain backward compatibility with existing formats

#### Scenario: Custom format detection
- **WHEN** implementing custom format detection logic
- **THEN** the dispatcher SHALL allow override of default detection
- **AND** SHALL support fallback to default behavior
- **AND** SHALL validate custom detection results