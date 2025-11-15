## ADDED Requirements

### Requirement: Versioned Transaction Log
The system SHALL maintain a monotonically increasing version number per dataset that identifies the committed state of that dataset in the catalog.

#### Scenario: Successful commit increments version
- **WHEN** a write operation successfully commits new data for a dataset
- **THEN** the system SHALL insert a new row into the `transactions` table with a unique `version` number greater than any previous version for that dataset
- **AND** it SHALL update the dataset’s `current_version` field to that same version.

### Requirement: Optimistic Concurrency Control for Writers
Writers SHALL use optimistic concurrency control: they must check the current dataset version before committing and fail with a conflict if it has changed.

#### Scenario: Two writers race to commit
- **WHEN** Writer A and Writer B both read the same current version of a dataset and attempt to write new data
- **AND** Writer A successfully commits first, advancing the dataset’s `current_version`
- **THEN** when Writer B attempts to commit using the stale base version
- **THEN** the system SHALL detect the version mismatch and reject Writer B’s commit with a concurrency conflict error
- **AND** Writer B SHALL be required to reload metadata and retry if desired.

### Requirement: Atomic Catalog Updates
Catalog updates for a single commit (including entries in `transactions`, `files`, `row_groups`, `partitions`, and the dataset’s `current_version`) SHALL be performed within a single database transaction so that they either all succeed or all fail.

#### Scenario: Failure rolls back catalog changes
- **WHEN** a failure occurs while updating catalog tables during a commit
- **THEN** the database transaction SHALL be rolled back
- **AND** no new `transactions` entry, file records, or version updates SHALL be visible in the catalog.

### Requirement: Locking Strategy Per Backend
The system SHALL define and apply a locking strategy appropriate to each supported catalog backend to prevent conflicting catalog updates during commits.

#### Scenario: Acquire exclusive commit lock
- **WHEN** a writer begins a commit for a dataset
- **THEN** it SHALL acquire an appropriate lock on that dataset’s catalog entries (e.g., advisory lock in PostgreSQL, exclusive write transaction in SQLite/DuckDB)
- **AND** it SHALL hold this lock until the commit transaction is completed or rolled back
- **AND** other writers attempting to commit concurrently SHALL either block or receive a conflict error according to backend capabilities.

