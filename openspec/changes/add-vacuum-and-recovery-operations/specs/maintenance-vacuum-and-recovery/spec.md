## ADDED Requirements

### Requirement: Vacuum Tombstoned and Unreferenced Files
The system SHALL provide a maintenance operation (`vacuum`) that can remove tombstoned or unreferenced files from storage after a configurable retention period.

#### Scenario: Vacuum removes old tombstones
- **WHEN** a dataset has files in storage that are not referenced by any active catalog version (tombstones)
- **AND** those files are older than the configured retention period
- **THEN** running `vacuum` for that dataset SHALL delete those files from storage
- **AND** it SHALL update any related catalog entries (e.g., marking them as deleted or removing them) as appropriate.

### Requirement: Retention Policy Enforcement
The system SHALL support a retention policy that delays deletion of tombstones to allow for recovery from recent failures or misconfigurations.

#### Scenario: Recent tombstones are preserved
- **WHEN** tombstoned files are younger than the configured retention period
- **THEN** `vacuum` SHALL leave those files in place
- **AND** it SHALL report them in logs or metrics as retained tombstones rather than deleting them.

### Requirement: Recovery of Catalog and Storage After Crashes
The system SHALL provide a recovery process that reconciles the catalog with the underlying storage after crashes or unexpected termination.

#### Scenario: Recovery marks stray files as tombstones
- **WHEN** recovery runs and finds Parquet files under a dataset’s `base_uri` that are not referenced by any catalog version
- **THEN** it SHALL mark those files as tombstones in the catalog (if not already marked)
- **AND** it SHALL schedule or mark them as candidates for deletion by subsequent `vacuum` operations.

#### Scenario: Recovery cleans up incomplete catalog records
- **WHEN** recovery runs and finds partially written catalog entries associated with a transaction that was never committed (e.g., no matching version in the transaction log)
- **THEN** it SHALL mark those entries as invalid or tombstoned according to the data model
- **AND** it SHALL ensure they do not appear in any future reads or version listings.

### Requirement: Observability of Maintenance Actions
Vacuum and recovery operations SHALL produce logs and/or metrics that summarize their actions for operators.

#### Scenario: Vacuum logs deleted and retained files
- **WHEN** `vacuum` completes for a dataset
- **THEN** the system SHALL log or emit metrics summarizing the number of files deleted, the number retained due to policy, and any errors encountered.

