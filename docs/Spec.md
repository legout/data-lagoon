# Technical Specification: Pythonic Parquet Lakehouse Library

## 1 Overview

This document specifies the architecture and detailed design of a Python library that provides ACID‑style management of Parquet datasets on object storage while offering a Pythonic API for reading and writing data.  The library uses Parquet for data storage and a SQL database (DuckDB, SQLite or PostgreSQL) for metadata.  It integrates with PyArrow/arro3 for low‑level I/O and supports high‑level querying via DuckDB, Polars and DataFusion.

## 2 Architecture

### 2.1 Components

1. **Client API Layer:** Exposes Python functions to write and read datasets.  Accepts Arrow `Table`, `RecordBatchReader`, Pandas DataFrame or Polars DataFrame as input.
2. **Metadata Store:** A relational database containing tables for `files`, `row_groups`, `schema_versions` and `transactions`.  This store supports ACID transactions and is the authoritative source of table state.
3. **Data Storage:** Parquet files stored in a target filesystem (local disk, S3, GCS, ADLS) via `fsspec`.  Files are immutable and named uniquely using UUID v7.
4. **Statistics Extractor:** Retrieves per‑file and per‑row‑group metadata during writes using either DuckDB’s `RETURN_STATS` or PyArrow’s `file_visitor` callback.
5. **Schema Manager:** Compares incoming data schemas with the catalog schema, performs merging or type promotion and records schema versions.
6. **Reader Engine:** Constructs `FileSystemDataset` objects from selected files and row groups and exposes them to compute engines (DuckDB, Polars, DataFusion).
7. **Transaction Manager:** Implements optimistic concurrency control and ensures atomic commits.

### 2.2 Flow Diagram

**Write Path:**

1. Client calls `write_dataset(data, dataset_uri, partition_by=…, schema_merge=True)`.  `data` is converted to an Arrow `Table` or `RecordBatchReader` if needed.
2. The schema manager loads the current schema from the catalog and attempts to merge with the new data’s schema.  If merge is disabled or fails, raise an error.
3. Data is partitioned and written to Parquet files using either:
   - **DuckDB:** `COPY (SELECT …) TO directory (FORMAT parquet, PARTITION_BY …, FILENAME_PATTERN '{uuidv7}', RETURN_STATS)`; the result includes file names, row counts and column statistics [oai_citation:8‡duckdb.org](https://duckdb.org/docs/stable/sql/statements/copy#:~:text=).
   - **PyArrow:** `dataset.write_dataset(data, base_dir, format='parquet', partitioning=…, file_visitor=callback)`.  The callback receives `WrittenFile` objects containing `path` and `metadata`, allowing the collector to capture file‑level stats [oai_citation:9‡arrow.apache.org](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.write_dataset.html#:~:text=could%20end%20up%20with%20very,small%20row%20groups).
4. A new transaction record is created in the metadata store with a unique version number and timestamp.  The files and row‑group statistics collected from the previous step are inserted into `files` and `row_groups` tables.  The transaction is committed using the database’s transaction mechanism.
5. The catalog’s current version pointer is updated to the new version.  Uncommitted or failed files remain on disk but are not referenced.

**Read Path:**

1. Client calls `read_dataset(dataset_uri, version=None, predicates=…)`.  If `version` is None, use the latest committed version.
2. Transaction manager retrieves the list of files and row groups from the catalog that belong to the specified version.  Apply predicate pushdown using stored statistics: only select row groups where predicate values overlap stored `min`/`max` statistics.
3. Build a list of PyArrow `ParquetFragment` objects.  For each fragment, attach a `partition_expression` or `filter` expression representing the predicate.
4. Create a `FileSystemDataset` from these fragments.  Return this dataset to the client or pass it to a compute engine (DuckDB `relation_from_arrow_dataset`, Polars `scan_pyarrow_dataset`, or DataFusion `SessionContext.read_parquet`).
5. The compute engine performs projection, filtering and aggregation; the library does not execute queries itself.

## 3 Database Schema

### 3.1 Tables

- **`datasets`** (`id`, `name`, `base_uri`, `current_version`, `created_at`)
- **`schema_versions`** (`id`, `dataset_id`, `version`, `arrow_schema`, `created_at`)
- **`transactions`** (`id`, `dataset_id`, `version`, `timestamp`, `operation`, `metadata_json`)
- **`files`** (`id`, `dataset_id`, `version`, `file_path`, `file_size_bytes`, `row_count`, `created_at`, `is_tombstoned`)
- **`row_groups`** (`id`, `file_id`, `row_group_index`, `stats_min_json`, `stats_max_json`, `null_counts_json`, `row_count`)
- **`partitions`** (`file_id`, `key`, `value`)

Indexes should be created on `files.version`, `files.file_path` and relevant partition columns to speed up lookups.

## 4 Schema Management

1. **Initial Creation:** When a new dataset is created, its schema is stored in `schema_versions` with version 0.
2. **Merging:** When `schema_merge=True`, the new Arrow schema is unified with the current schema.  If a field is missing in the incoming data, it will be added with nullable type.  If a field exists with a different type, type promotion is attempted (e.g. `int32` → `int64`, `int`/`float` → `decimal`, any type → `string`).  Otherwise, raise an error.
3. **Type Promotion Flag:** A per‑dataset or per‑write flag allows automatic promotion to `string/utf8` when mismatched types cannot be merged.
4. **Versioning:** Each schema change increments the `schema_versions.version`.  Files record which schema version they adhere to.

## 5 File Naming and Tombstones

- **Naming Scheme:** Each file is named using a UUID v7 (ISO 8601 timestamp with random suffix) to ensure lexical ordering and uniqueness.  DuckDB supports this via `FILENAME_PATTERN '{uuid}'` or `{uuidv7}` [oai_citation:10‡duckdb.org](https://duckdb.org/docs/stable/data/partitioning/partitioned_writes#:~:text=%60FILENAME_PATTERN%60%20a%20pattern%20with%20%60,defined%20to%20create%20specific%20filenames).
- **Tombstoned Files:** Files that were written by aborted transactions remain on the filesystem but have no entry in the catalog or are marked `is_tombstoned=True`.  A background vacuum process scans for such files and deletes them based on retention policies.

## 6 Statistics Extraction

- **DuckDB:** When using `COPY` to write, pass `RETURN_STATS = true`.  DuckDB returns a result set with `filename`, `row_count`, `file_size_bytes`, `footer_size_bytes`, and `column_statistics` (an object mapping each column name to its `min`, `max`, `column_size_bytes` and `null_count`) [oai_citation:11‡duckdb.org](https://duckdb.org/docs/stable/sql/statements/copy#:~:text=).  Parse this into the `files` and `row_groups` tables.
- **PyArrow:** Use the `file_visitor` callback.  Each `WrittenFile.metadata` contains a `parquet.FileMetaData` object which lists row groups and column statistics [oai_citation:12‡arrow.apache.org](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.write_dataset.html#:~:text=could%20end%20up%20with%20very,small%20row%20groups).  Iterate over row groups and extract `min`, `max`, `null_count` for each column; if row group statistics are missing, treat them as `None`.  Store this in the catalog.

## 7 Read‑Side Optimisations

- **Predicate Pushdown:** During reads, construct a SQL query (e.g. `SELECT file_id, row_group_index FROM row_groups WHERE stats_min <= <filter_value> AND stats_max >= <filter_value>`).  Only return row groups that may contain matching rows.
- **Partition Pruning:** When datasets are partitioned by columns (e.g. `date`), store partition key/value pairs in the `partitions` table.  Prune entire files by matching partition values against predicates.
- **Fragment Construction:** For each selected file, create a PyArrow `ParquetFragment` with a `partition_expression` representing the combined predicate; this instructs PyArrow to skip non‑matching row groups.  Use `pyarrow.dataset.dataset_from_fragments` or `FileSystemDataset.from_fragments`.
- **Compute Engine Integration:**
  - **DuckDB:** Use `duckdb.query('SELECT … FROM read_parquet(file_paths, row_group_filter=?)')` or create a relation via the DuckDB Python API’s `from_arrow_dataset`.
  - **Polars:** Use `pl.scan_pyarrow_dataset(dataset)`, which preserves predicate pushdown.
  - **DataFusion:** Use `SessionContext.read_parquet_glob(files)` and set logical predicates; DataFusion’s optimizer pushes down filters using row‑group statistics.

## 8 Concurrency & Transactions

1. **Version Numbers:** Each commit increments the dataset’s version number.  Writers must check the current version before committing; if it has changed, they must reload metadata and retry.
2. **Atomic Updates:** Catalog updates and file writes occur in a single database transaction.  If the write fails, the transaction is rolled back and no new version is recorded.  Unreferenced files remain as tombstones.
3. **Locking:** Use advisory locks (e.g. `SELECT pg_advisory_lock`) in PostgreSQL or exclusive transactions in SQLite/DuckDB to prevent two writers from updating the catalog simultaneously.

## 9 Error Handling & Recovery

- **Partial Writes:** If the process crashes after files are written but before committing the catalog, the uncommitted files are tombstoned.
- **Schema Mismatch:** If schema merging is disabled and the new data’s schema differs, raise a `SchemaMismatchError`.
- **Database Failure:** If the metadata database is unreachable during commit, abort the write and leave files tombstoned.
- **Recovery on Startup:** On library startup, scan the `files` table for any records not referenced by the current version; mark them as tombstoned and schedule them for deletion.

## 10 Testing & Validation

- **Unit Tests:** Validate schema merging logic, file naming, transaction boundaries, and catalog queries.
- **Integration Tests:** Write and read datasets under various configurations (partitioning, schema changes, failures, concurrent writes) using local and remote file systems.
- **Benchmarking:** Compare read performance with and without predicate pruning on large datasets.  Validate that reading with filters uses fewer row groups and reduces I/O.
- **Durability Tests:** Simulate crashes at different stages of write to ensure no committed version becomes corrupted.

## 11 Open Questions and Future Work

- **Upserts and Merge:** Support for row‑level updates (like Delta’s `MERGE INTO`) would require additional structures (delete vectors) and is considered out of scope for the initial release.
- **Streaming ingestion:** Real‑time ingestion from Kafka or similar could be added by buffering micro‑batches and committing them atomically.
- **Metadata Service:** As datasets grow, a dedicated metadata service (e.g. REST API) may replace the embedded SQL database for scaling.

## 12 Conclusion

This specification outlines a Python library that brings lakehouse‑style management to Parquet files without relying on JVM frameworks.  By leveraging row‑group statistics and a SQL‑backed transaction log, it achieves fast reads and reliable writes.  Integrating with PyArrow, DuckDB and Polars ensures broad ecosystem compatibility, while unique file names and tombstone management keep object storage clean.
