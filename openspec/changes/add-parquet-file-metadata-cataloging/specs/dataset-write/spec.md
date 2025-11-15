## MODIFIED Requirements

### Requirement: File Visitor MUST Persist Complete Metadata
`write_dataset` SHALL persist the complete metadata provided by PyArrow’s `WrittenFile.metadata` (schema, row groups, column stats, partition values) into the catalog as part of each commit.

#### Scenario: Metadata persisted atomically with commit
- **WHEN** `write_dataset` finishes writing files and before the transaction commits
- **THEN** it SHALL insert/ update the `schema_versions`, `files`, `row_groups`, and `partitions` tables with the metadata captured from every file
- **AND** it SHALL perform these inserts within the same database transaction as the version update so metadata and version state cannot diverge.
