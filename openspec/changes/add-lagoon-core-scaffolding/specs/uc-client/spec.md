## ADDED Requirements
### Requirement: Unity Catalog Client Integration
The system SHALL provide a Unity Catalog client wrapper that uses the official unitycatalog-python SDK for all metadata operations, ensuring compatibility and proper error handling.

#### Scenario: Retrieve table metadata by full name
- **WHEN** UCClient.get_table("catalog.schema.table") is called
- **THEN** client SHALL return complete table metadata
- **AND** result SHALL include format, location, and schema information
- **AND** UnityCatalogException SHALL be mapped to Lagoon exceptions

#### Scenario: List tables in schema
- **WHEN** UCClient.list_tables("catalog", "schema") is called
- **THEN** client SHALL return list of table metadata
- **AND** each item SHALL include basic table information
- **AND** empty list SHALL be returned for non-existent schemas

#### Scenario: Create external table
- **WHEN** UCClient.create_external_table() is called with valid parameters
- **THEN** table SHALL be created in Unity Catalog
- **AND** external location SHALL be properly registered
- **AND** columns SHALL be defined when provided
- **AND** creation errors SHALL be raised with descriptive messages

#### Scenario: Drop table
- **WHEN** UCClient.drop_table("catalog.schema.table") is called
- **THEN** table SHALL be removed from Unity Catalog
- **AND** operation SHALL succeed for both managed and external tables
- **AND** non-existent tables SHALL raise appropriate errors

### Requirement: Client Configuration and Authentication
The system SHALL provide secure Unity Catalog client configuration with proper authentication handling and connection validation.

#### Scenario: Initialize client with token authentication
- **WHEN** UCClient is created with UC URL and token
- **THEN** client SHALL establish connection to Unity Catalog
- **AND** authentication SHALL be validated during initialization
- **AND** connection errors SHALL be raised immediately

#### Scenario: Handle authentication failures
- **WHEN** invalid credentials are provided
- **THEN** UCClient SHALL raise UnityCatalogException
- **AND** error SHALL be mapped to Lagoon CatalogError
- **AND** original error details SHALL be preserved for debugging
