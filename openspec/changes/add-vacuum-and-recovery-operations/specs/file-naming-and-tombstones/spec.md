## MODIFIED Requirements

### Requirement: Tombstones Persist Until Vacuum
Tombstoned files SHALL remain in storage and in the catalog (if represented there) until explicitly removed by the `vacuum` maintenance operation, subject to retention policies.

#### Scenario: Tombstoned files survive restarts
- **WHEN** a write fails or a transaction is rolled back, leaving files unreferenced by any committed version
- **AND** the system restarts one or more times
- **THEN** those files SHALL remain in storage as tombstones until a `vacuum` run deletes them according to policy
- **AND** they SHALL remain invisible to readers during this time.

### Requirement: Clear Lifecycle for Tombstoned Files
The lifecycle of tombstoned files SHALL be: created during failed or superseded writes, made invisible to readers via the catalog, and eventually deleted by vacuum after the retention period.

#### Scenario: Tombstone lifecycle from creation to deletion
- **WHEN** a file is created during a write that never commits a new version
- **THEN** it SHALL be considered a tombstone (unreferenced file)
- **AND** recovery MAY mark or reinforce this status in the catalog
- **AND** a later `vacuum` operation MAY delete it permanently from storage once the retention period has elapsed.

