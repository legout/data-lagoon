## ADDED Requirements

### Requirement: Unit Test Coverage for Core Components
Core components (schema management, catalog operations, transaction manager, storage abstraction) SHALL be covered by unit tests that validate their behavior in isolation.

#### Scenario: Unit tests for schema and transactions
- **WHEN** changes are made to schema merge logic or transaction handling
- **THEN** existing unit tests SHALL continue to pass or be updated to reflect new intended behavior
- **AND** new tests SHALL be added for new edge cases or configuration options.

### Requirement: Integration Tests for End-to-End Flows
The system SHALL include integration tests that cover end-to-end flows across multiple capabilities.

#### Scenario: End-to-end write/read with pruning
- **WHEN** an integration test writes a partitioned dataset with statistics to a local or in-memory backend
- **AND** then reads it back with filters using `read_dataset` and engine helpers
- **THEN** the test SHALL verify that:
  - The returned data matches expected results
  - The catalog was populated with expected statistics and partitions
  - The number of files/row groups read is less than or equal to a full scan when predicates are selective.

### Requirement: Durability and Crash Simulation Tests
The system SHALL include tests that simulate crashes or failures at critical points in the write path to validate durability guarantees.

#### Scenario: Crash after files written but before catalog commit
- **WHEN** a test simulates a crash after writing Parquet files but before committing catalog changes
- **THEN** upon recovery, the system SHALL not expose these files as part of any committed version
- **AND** they SHALL be treated as tombstones and eligible for deletion by `vacuum`.

### Requirement: Performance Benchmarks for Pruned vs Full Scans
The system SHALL include basic benchmarks that compare read performance with and without catalog-based pruning on representative datasets.

#### Scenario: Benchmark selective reads
- **WHEN** a benchmark reads a dataset using a selective predicate with pruning enabled
- **AND** the same dataset is read without pruning (e.g., full directory scan)
- **THEN** the benchmark SHALL record metrics (e.g., elapsed time, bytes read, row groups scanned)
- **AND** these metrics SHALL demonstrate that the pruned read is significantly more efficient for selective predicates, consistent with PRD goals.

### Requirement: Test and Benchmark Maintenance
When core behavior changes (e.g., transaction semantics, pruning logic, schema rules), tests and benchmarks SHALL be updated to reflect new expected behavior and prevent regressions.

#### Scenario: Update tests after behavior change
- **WHEN** a change modifies how pruning works or how versions are allocated
- **THEN** existing tests and benchmarks that depend on this behavior SHALL be reviewed and updated
- **AND** new tests SHALL be added as needed to cover new edge cases or invariants.

