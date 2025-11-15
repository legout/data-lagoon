## Why

The catalog currently supports only SQLite and (optionally) DuckDB, which limits how the library can be used in production environments that require shared networked catalogs and stronger concurrency guarantees. PostgreSQL is explicitly called out as a target backend in the PRD/Spec. Adding a first-class Postgres connector for the catalog will enable multi-writer deployments, hosted catalog services, and easier scaling.

## What Changes

- Implement a PostgreSQL catalog connector that:
  - Understands a `postgresql://` (or `postgres://`) connection URI.
  - Creates catalog tables using Postgres-compatible DDL (e.g., `SERIAL`/`BIGSERIAL`, `TIMESTAMPTZ`, appropriate indexes).
  - Uses Postgres advisory locks or row-level locking strategies described in the transactions/concurrency spec.
  - Handles binary Arrow schema storage (e.g., `bytea` column) and JSON metadata using `jsonb`.
- Update the `catalog-store` spec to document Postgres backend requirements and locking behavior.

## Impact

- Affected specs: `catalog-store` (MODIFIED / ADDED Postgres backend section) and `transactions-and-concurrency` (references to advisory locks; might be cross-linked).
- Code: new Postgres connector module or extension of existing `connect_catalog`; migrations/DDL; integration tests hitting Postgres (possibly via Docker/CI).

