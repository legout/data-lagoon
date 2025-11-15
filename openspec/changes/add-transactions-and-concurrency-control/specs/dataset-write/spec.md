## MODIFIED Requirements

### Requirement: Version-Aware Writes
`write_dataset` SHALL operate in a version-aware manner: each write is prepared against a specific base version and SHALL fail if the catalog’s current version has changed since that base version was read.

#### Scenario: Write with unchanged base version
- **WHEN** a client calls `write_dataset` and specifies (explicitly or implicitly) the dataset’s base version
- **AND** the catalog’s `current_version` still matches that base version when the commit is attempted
- **THEN** the system SHALL proceed with the commit
- **AND** it SHALL record a new transaction with an incremented version.

#### Scenario: Write with stale base version
- **WHEN** a client calls `write_dataset` based on an earlier snapshot of the catalog
- **AND** another writer has already advanced the dataset’s `current_version`
- **THEN** the system SHALL reject the new commit with a concurrency conflict error
- **AND** it SHALL NOT create a new version or update catalog entries for that write.

### Requirement: Single-Transaction Catalog Commit
`write_dataset` SHALL group all catalog updates for a commit into a single database transaction together with the version update.

#### Scenario: Atomic commit of metadata
- **WHEN** `write_dataset` has finished writing data files and is ready to commit metadata
- **THEN** it SHALL open a database transaction
- **AND** within that transaction it SHALL insert the transaction record, file/row-group/partition records, and update `datasets.current_version`
- **AND** it SHALL commit or roll back this transaction as a single unit.

