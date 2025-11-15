## MODIFIED Requirements

### Requirement: PostgreSQL Catalog Backend Support
The catalog SHALL support PostgreSQL as a backend alongside SQLite and DuckDB, using `postgresql://` (or `postgres://`) URIs.

#### Scenario: Connect catalog to PostgreSQL
- **WHEN** a client calls the catalog connection factory with a Postgres URI
- **THEN** the system SHALL establish a connection using the configured credentials
- **AND** it SHALL create the catalog tables using Postgres-compatible DDL if they do not already exist.

### Requirement: Postgres-Specific Schema Definitions
Catalog tables in Postgres SHALL use appropriate column types:
- `BIGSERIAL`/`SERIAL` for IDs
- `TIMESTAMPTZ` for timestamps
- `BYTEA` for Arrow schemas
- `JSONB` for metadata JSON fields
- Indexes on frequently queried columns (`datasets.name`, `files.version`, etc.).

#### Scenario: Create schema in Postgres
- **WHEN** the catalog schema initialization runs on Postgres
- **THEN** each table SHALL be created with the Postgres-specific column types listed above
- **AND** indexes SHALL be created to match the performance expectations in the spec.

### Requirement: Advisory Locks for Postgres Commits
When using Postgres, the system SHALL use advisory locks (e.g., `pg_advisory_lock`) to coordinate writers during commits as described in the transactions/concurrency spec.

#### Scenario: Acquire advisory lock per dataset
- **WHEN** a writer begins a commit in Postgres
- **THEN** it SHALL acquire a dataset-specific advisory lock before updating catalog tables
- **AND** it SHALL release the lock after the transaction commits or rolls back.
