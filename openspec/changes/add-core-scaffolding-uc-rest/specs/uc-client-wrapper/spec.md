## ADDED Requirements

### Requirement: Unity Catalog Client Initialization
The system SHALL provide a `UCClient` class that wraps the official `unitycatalog-python` SDK.

#### Scenario: Initialize UC client with authentication
- **WHEN** creating a UCClient instance
- **THEN** the constructor SHALL accept a UC host URL
- **AND** SHALL accept an optional authentication token
- **AND** SHALL initialize the underlying UnityCatalogClient
- **AND** SHALL raise ConnectionError if the host is invalid

#### Scenario: Initialize UC client without token
- **WHEN** creating a UCClient without a token
- **THEN** the client SHALL attempt anonymous access
- **AND** SHALL work with local UC instances that don't require authentication

### Requirement: Table Retrieval Operations
The system SHALL provide methods to retrieve table information from Unity Catalog.

#### Scenario: Get single table metadata
- **WHEN** calling get_table() with a fully qualified table name
- **THEN** the method SHALL return a dictionary with table metadata
- **AND** SHALL include data_source_format, storage_location, and schema information
- **AND** SHALL raise CatalogError if the table doesn't exist
- **AND** SHALL raise CatalogError if the table name format is invalid

#### Scenario: List tables in schema
- **WHEN** calling list_tables() with catalog and schema names
- **THEN** the method SHALL return a list of table dictionaries
- **AND** each dictionary SHALL include table name, format, and basic metadata
- **AND** SHALL return an empty list if no tables exist
- **AND** SHALL raise CatalogError if the catalog or schema doesn't exist

### Requirement: Table Management Operations
The system SHALL provide basic table creation and deletion capabilities.

#### Scenario: Create minimal external table
- **WHEN** calling create_table() with table specification
- **THEN** the method SHALL create an external table in Unity Catalog
- **AND** SHALL accept table name, storage location, format, and optional column definitions
- **AND** SHALL return the created table metadata
- **AND** SHALL raise CatalogError if creation fails
- **AND** SHALL raise ValidationError if required parameters are missing

#### Scenario: Drop existing table
- **WHEN** calling drop_table() with a fully qualified table name
- **THEN** the method SHALL delete the table from Unity Catalog
- **AND** SHALL not delete the underlying data files (external table behavior)
- **AND** SHALL raise CatalogError if the table doesn't exist
- **AND** SHALL complete silently if the table is successfully dropped

### Requirement: Error Handling and Translation
The system SHALL translate Unity Catalog exceptions into consistent Lagoon errors.

#### Scenario: Handle authentication failures
- **WHEN** Unity Catalog returns authentication errors
- **THEN** UCClient SHALL raise CatalogError with authentication details
- **AND** SHALL preserve the original error context

#### Scenario: Handle network connectivity issues
- **WHEN** network requests to Unity Catalog fail
- **THEN** UCClient SHALL raise ConnectionError
- **AND** SHALL include retry suggestions in the error message

#### Scenario: Handle malformed API responses
- **WHEN** Unity Catalog returns unexpected response formats
- **THEN** UCClient SHALL raise CatalogError
- **AND** SHALL include response details for debugging

### Requirement: Client Configuration
The system SHALL support flexible client configuration options.

#### Scenario: Configure timeout settings
- **WHEN** initializing UCClient
- **THEN** the constructor SHALL accept optional timeout parameters
- **AND** SHALL apply timeouts to all API calls
- **AND** SHALL use sensible defaults if not specified

#### Scenario: Configure retry behavior
- **WHEN** making API calls that fail transiently
- **THEN** UCClient SHALL automatically retry on network errors
- **AND** SHALL use exponential backoff for retries
- **AND** SHALL limit the maximum number of retry attempts