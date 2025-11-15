## MODIFIED Requirements

### Requirement: Schema Validation on Write
Before writing any data files, `write_dataset` SHALL validate the incoming data’s schema against the catalog schema for the target dataset and apply schema management rules.

#### Scenario: Write with matching schema
- **WHEN** a client calls `write_dataset` for a dataset whose catalog schema matches the incoming data’s schema
- **THEN** the system SHALL proceed with the write using the existing schema version
- **AND** it SHALL record the existing schema version on all new files.

#### Scenario: Write with new columns and merge enabled
- **WHEN** a client calls `write_dataset` with data that includes additional columns
- **AND** `schema_merge=True`
- **THEN** the system SHALL invoke the schema management component to merge schemas
- **AND** if the merge succeeds, it SHALL create a new schema version and proceed with the write
- **AND** if the merge fails due to incompatible types, it SHALL raise a schema error and abort the write.

### Requirement: Reject Incompatible Writes When Merge Disabled
When `schema_merge=False`, any schema differences between the incoming data and the catalog schema SHALL cause the write to fail before any new version is committed.

#### Scenario: Strict mode write with different schema
- **WHEN** a client calls `write_dataset` for a dataset whose current schema differs from the incoming schema
- **AND** `schema_merge=False`
- **THEN** the system SHALL reject the write with a clear schema mismatch error
- **AND** it SHALL leave the catalog and data files unchanged.

