## ADDED Requirements

### Requirement: Schema Versioning
The system SHALL maintain a versioned history of dataset schemas in the `schema_versions` table and associate each data file with the schema version under which it was written.

#### Scenario: Record new schema version
- **WHEN** a write operation detects that the incoming schema differs from the current schema in a way that is allowed (e.g., new columns added)
- **THEN** the system SHALL create a new entry in `schema_versions` with an incremented `version` number and the merged Arrow schema
- **AND** it SHALL record that new schema version identifier on all files produced by that write.

### Requirement: Schema Merge Behavior
When `schema_merge=True`, the system SHALL attempt to merge the incoming Arrow schema with the current catalog schema.

#### Scenario: Add new nullable column
- **WHEN** the incoming data contains a new column that does not exist in the current schema
- **AND** `schema_merge=True`
- **THEN** the system SHALL add the new column to the merged schema as nullable
- **AND** it SHALL write new files with the merged schema and record the updated schema version in the catalog.

#### Scenario: Type widening promotion
- **WHEN** the incoming data has a column whose type can be widened without loss (e.g., `int32` to `int64`)
- **AND** schema merging and type promotion are permitted by configuration
- **THEN** the system SHALL promote the column type in the merged schema
- **AND** it SHALL persist the promoted type in the new schema version.

### Requirement: Strict Mode and Schema Mismatch Errors
When schema merging is disabled or a schema change cannot be reconciled under the configured promotion rules, the system SHALL reject the write before creating any new committed version.

#### Scenario: Incompatible type without promotion
- **WHEN** the incoming data has a column with a type that is incompatible with the existing schema (e.g., `string` vs `struct`)
- AND `schema_merge=False` or promotion to `string/utf8` has been disabled
- **THEN** the system SHALL raise a `SchemaMismatchError` (or equivalent)
- **AND** it SHALL NOT create new files or catalog entries for that write.

#### Scenario: Promotion to string/utf8
- **WHEN** configuration allows “last-resort” promotion to `string/utf8`
- **AND** the incoming and existing column types cannot be reconciled by normal widening rules
- **THEN** the system MAY promote both to `string/utf8` if enabled
- **AND** it SHALL record this decision in the merged schema and the catalog.

