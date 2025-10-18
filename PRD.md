# PRD — data-lagoon (import: `lagoon`)

## Vision
`data-lagoon` (import path `lagoon`) provides a **unified Python API** to discover, read, write, query, and manage **Unity Catalog–registered** tables regardless of storage format (Delta, Iceberg, Parquet) or backend (S3, R2, MinIO/SeaweedFS, local).

## Objectives
- Single, typed API: `lagoon.read()`, `lagoon.write()`, `lagoon.sql()`.
- Format-aware routing: Delta (delta-rs), Iceberg (PyIceberg), Parquet (PyArrow).
- Catalog-aware: resolve by `catalog.schema.table` via UC REST.
- Query engines: DuckDB (default), DataFusion (optional), Ibis (expressions).
- S3-compatible support: endpoint, path-style, creds.

## Architecture
```
src/lagoon/
  core.py          # Base abstractions (TableMetadata, BaseTable facade)
  client.py        # Unity Catalog REST client (httpx)
  dispatch.py      # Router -> proper adapter by format
  adapters/
    base.py        # Protocol for adapters
    delta_rs.py    # Delta Lake via deltalake
    pyiceberg_.py  # Iceberg via PyIceberg (REST catalog)
    pyarrow_.py    # Parquet via PyArrow
    polars_.py     # Helpers for Polars interchange
    duckdb_.py     # SQL engine facade
    datafusion_.py # optional
    ibis_.py       # optional
```

## API (initial surface)
```python
from lagoon import Lagoon

lg = Lagoon(uc_url="http://localhost:8080",
            s3_endpoint="http://seaweed-s3:8333",
            s3_region="us-east-1",
            access_key="...",
            secret_key="...")

t = lg.get_table("unity.default.sales")     # returns BaseTable
df = t.to_polars()
lg.write(df, "unity.default.sales_copy", format="delta", mode="overwrite")
res = lg.sql("SELECT * FROM unity.default.sales LIMIT 5")
```

## Phases
1) Core scaffolding + UC REST client + dispatcher.
2) Delta & Parquet adapters (read/write); S3 config helper.
3) Iceberg adapter via UC Iceberg REST; DuckDB query layer; Lagoon facade.
4) DataFusion & Ibis (optional); CLI; docs.
