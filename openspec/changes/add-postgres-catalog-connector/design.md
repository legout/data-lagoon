## Context
- Adds PostgreSQL as a catalog backend to support multi-writer, network-accessible deployments.
- Relies on prior transaction/locking design.

## Goals
- Parse `postgresql://` URIs and establish connections via `psycopg` (or async variant).
- Create catalog schema using Postgres types (`BIGSERIAL`, `TIMESTAMPTZ`, `BYTEA`, `JSONB`).
- Implement advisory lock helpers for dataset-level commit locking.
- Ensure Arrow schema serialization works with `BYTEA`.
- Provide integration tests (possibly via Docker or embedded Postgres).

## Design Overview

### Connection Factory
- Extend `connect_catalog` to recognize `postgresql`/`postgres` schemes.
- Use DSN parsing to extract host/port/db/user/password.
- Optionally support connection pooling via `psycopg_pool`.

### Schema Initialization
- SQL templates tailored to Postgres (no `AUTOINCREMENT`).
- Create indexes on:
  - `datasets(name)`, `datasets(base_uri)`
  - `files(dataset_id, version)`
  - `row_groups(file_id)`
- Ensure `schema_versions.arrow_schema` uses `BYTEA`.
- `transactions.metadata_json` uses `JSONB`.

### Advisory Locks
- Expose helper:
  ```python
  def acquire_dataset_lock(conn, dataset_id):
      conn.execute("SELECT pg_advisory_lock(%s)", (dataset_id,))
  ```
- Use `pg_advisory_unlock` on completion.

### Testing
- Provide optional test suite requiring Postgres (skip if DSN not set).
- Use temp database or ephemeral schema for isolation.

## Risks
- Adding psycopg dependency increases install size; consider making it optional extra (`data-lagoon[postgres]`).
- Need to handle network errors gracefully (retry logic or propagate error).

## Open Questions
- Should we support SSL options or rely on DSN parameters? (Probably rely on DSN.)
- How to rotate advisory lock keys if dataset_id exceeds `int32`? Use 64-bit version of advisory locks (pass dataset_id as BIGINT).
