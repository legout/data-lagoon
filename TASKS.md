# TASKS — data-lagoon

## Phase 1 — Core scaffolding + UC REST
- [ ] `TableMetadata` (dataclass) + `BaseTable` facade.
- [ ] `UCClient` with `get_table`, `list_tables`, `create_table` (min), `drop_table`.
- [ ] `TableAdapter` Protocol (to_arrow, to_polars, write, delete).
- [ ] `dispatch.build_table` routing (DELTA/ICEBERG/PARQUET).
- [ ] Tests (`respx` for UC client; routing tests).
- [ ] ruff + mypy + pytest all green.

## Phase 2 — Delta & Parquet
- [ ] `adapters/delta_rs.py` (deltalake) read/write -> Arrow/Polars.
- [ ] `adapters/pyarrow_.py` (pyarrow parquet) read/write -> Arrow/Polars.
- [ ] Shared S3 helper (endpoint, path-style, creds).
- [ ] Round-trip tests.

## Phase 3 — Iceberg + Query
- [ ] `adapters/pyiceberg_.py` against UC Iceberg REST.
- [ ] `adapters/duckdb_.py` for SQL (`Lagoon.sql()`).
- [ ] `Lagoon` facade with `read`, `write`, `sql` conveniences.

## Phase 4 — Optional
- [ ] DataFusion + Ibis adapters; backend flag.
- [ ] CLI, docs, CI.
