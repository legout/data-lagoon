## MODIFIED Requirements

### Requirement: File Visitor Metadata Persistence
The dataset writer’s metadata (`WrittenFile.metadata`) SHALL be persisted in the catalog so that downstream features (pruning, schema evolution) have accurate information without re-reading Parquet footers.

#### Scenario: Store schema fingerprint per file
- **WHEN** a file is written and the file visitor is invoked
- **THEN** the system SHALL record the schema (or schema version ID) associated with that file
- **AND** it SHALL store a reference to the appropriate `schema_versions` row.
