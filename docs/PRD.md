# Product Requirements Document: Pythonic Parquet Lakehouse Library

## Overview

**Project name:** Pythonic Parquet Lakehouse Library (working title)

**Purpose:** Build a pure‑Python library that manages partitioned Parquet datasets on object storage (AWS S3, Azure Data Lake Storage, Google Cloud Storage, local file systems) with ACID‑style semantics and efficient query support. The library will provide simple, Pythonic APIs for writing and reading data, maintain a transactional catalog in a SQL database (DuckDB, SQLite or PostgreSQL), and expose high‑level DataFrame–like interfaces while remaining interoperable with PyArrow, Polars, DuckDB, DataFusion and Daft.

## Problem Statement

Existing data lake solutions like Delta Lake and Apache Iceberg offer ACID guarantees and metadata‑rich query capabilities but depend on JVM ecosystems or complex infrastructures.  Python data scientists often work directly with Parquet files using PyArrow, Pandas or Polars; these tools provide no transaction guarantees and concurrent writes can corrupt data [oai_citation:0‡arrow.apache.org](https://arrow.apache.org/docs/python/dataset.html#:~:text=A%20note%20on%20transactions%20%26,ACID%20guarantees).  Users need a Python‑native solution that combines the reliability of a lakehouse with the simplicity of writing Parquet files.

## Goals and Objectives

- **ACID semantics:** Ensure that multi‑file writes are atomic and isolated. Readers should only see committed versions. The system must manage tombstone files and enable recovery from failed writes.
- **Metadata‑rich catalog:** Maintain a SQL‑backed catalog storing dataset schemas, file lists, partition values, row‑group statistics and transaction history. Metadata operations should be fast and support predicate pruning and time‑travel queries.
- **Pythonic API:** Provide an ergonomic API built around PyArrow, arro3 or Polars objects, avoiding JVM dependencies. Support optional SQL querying via DuckDB/DataFusion.
- **Interoperability:** Accept data from any Arrow‑compatible library, produce outputs that can be consumed by DuckDB, Polars, Pandas and Daft, and support reading existing Parquet datasets.
- **Scalability:** Efficiently handle datasets with millions of row groups, both locally and on cloud storage.

## Stakeholders

- **Data Scientists and ML Engineers:** Need to ingest and query large datasets using Python without relying on Spark or JVM frameworks.
- **Data Engineers:** Require robust pipelines for ingesting data into data lakes and performing ETL tasks in Python.
- **Researchers/Developers:** Interested in experimenting with open lakehouse designs or building custom formats on top of Parquet.

## User Stories

1. **Writer:** As a data engineer, I want to append a Pandas/Polars/Arrow table to a Parquet dataset on S3 such that if the write fails, no partial files remain visible.  I should be able to control partitioning and row‑group size.  After write, metadata (file path, row count, row‑group statistics, partition values) should be returned automatically and recorded in the catalog.
2. **Reader:** As a data scientist, I want to load a version of a dataset filtered on date and product columns.  The library should use stored statistics to skip irrelevant files or row groups for fast queries.  I can then hand the dataset to DuckDB or Polars for analysis.
3. **Schema Evolver:** As a developer, I want to add columns to an existing dataset without rewriting old data.  The library should merge schemas, optionally promoting mismatched types to string and raising errors when incompatible columns are added.
4. **Administrator:** As an admin, I need to vacuum tombstoned files left behind by failed or obsolete transactions to keep storage clean.

## Functional Requirements

1. **Metadata collection on write:**
   - When using DuckDB, support a `RETURN_STATS` option so the `COPY … TO …` command returns a table with file name, row count and `column_statistics` (min/max/null count per column) [oai_citation:1‡duckdb.org](https://duckdb.org/docs/stable/sql/statements/copy#:~:text=).
   - When using PyArrow, accept a `file_visitor` callback that receives a `WrittenFile` object for each created Parquet file containing both its path and metadata [oai_citation:2‡arrow.apache.org](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.write_dataset.html#:~:text=could%20end%20up%20with%20very,small%20row%20groups).
   - Capture partition values, row‑group statistics and file sizes.  Persist them in the catalog alongside transaction information.

2. **Catalog management:**
   - Maintain tables for files, row groups, schema versions and transactions.
   - Support snapshot reads at a given version and allow time‑travel queries.
   - Provide API functions to vacuum tombstoned files not referenced in any active version.

3. **Schema enforcement and merging:**
   - Store dataset schema in the catalog.
   - On writes, compare new data’s schema with the catalog schema.  If columns are missing, add them.  If types differ, optionally cast to string/UTF‑8; otherwise reject the write.
   - Provide a parameter to enable or disable automatic schema merging.

4. **File naming and tombstones:**
   - Generate unique file names for all Parquet files using UUID v7 (timestamp‑sortable).  DuckDB supports this via `FILENAME_PATTERN` with `{uuid}` or `{uuidv7}` [oai_citation:3‡duckdb.org](https://duckdb.org/docs/stable/data/partitioning/partitioned_writes#:~:text=%60FILENAME_PATTERN%60%20a%20pattern%20with%20%60,defined%20to%20create%20specific%20filenames).
   - Avoid temporary directories; rely on the transaction log to reference only committed files.  Unreferenced files become tombstones and can be vacuumed.

5. **Reading and query integration:**
   - Build a PyArrow `FileSystemDataset` from a list of selected files and row‑group predicates.  Use `make_fragment` with `partition_expression` to attach partition and predicate filters.
   - Expose the dataset to query engines (DuckDB, Polars, DataFusion) via connectors.
   - Provide direct Python filtering on the dataset through PyArrow’s dataset API.

6. **Concurrency and recovery:**
   - Use database transactions to ensure atomic catalog updates and file creations.  Implement optimistic concurrency control (check current version before committing a new version).  Provide recovery on restart by scanning for tombstones and uncommitted transactions.

## Non‑Functional Requirements

- **Performance:** Reading with column pruning and row‑group skipping should significantly outperform naive Parquet scans.  Metadata operations must be fast even with thousands of files.
- **Reliability:** No partial files should be visible after crashes; recovery mechanisms should clean up tombstones.
- **Portability:** Should run on Linux, macOS and Windows.  Support for remote object stores via `fsspec`.
- **Extensibility:** Architecture should allow plugging in alternative catalog backends (e.g. CloudSQL, DuckDB) and compute engines.

## Constraints & Assumptions

- Parquet files are immutable once written.  Updates are implemented as file inserts/deletes.
- The library will not implement streaming upserts or change‑data‑capture initially.
- Concurrent writes are serialized via transaction versioning; no two writers commit the same version.

## Success Metrics

- **Correctness:** No visible inconsistent states in presence of concurrent writes or crashes.
- **Performance:** Query latency at least 2× faster than scanning the entire Parquet directory when selective predicates are applied.
- **Ease of use:** Time for a user to append and query data should be comparable to existing PyArrow or DuckDB calls.
- **Adoption:** Number of downloads / GitHub stars (if open‑sourced) or positive user feedback.

## Risks & Mitigations

- **Handling large numbers of small files:** Too many files can slow down reads and metadata operations.  Mitigate with compaction operations and recommended row‑group sizes.
- **Schema drift:** Automatic promotion of types may lead to inconsistent typing.  Provide clear warnings and configuration options.
- **Object store eventual consistency:** Uncommitted files may appear during listing.  Rely on the catalog for visibility and schedule regular clean‑up.

## Timeline & Milestones

1. **MVP (6 weeks):** Basic write/read APIs, metadata store with schema and file list, single‑writer transaction log.
2. **Statistics & Pruning (4 weeks):** Collect row‑group stats via `RETURN_STATS`/`file_visitor`, implement file pruning in reads.
3. **Schema Evolution (3 weeks):** Schema merge, type promotion, optional strict mode.
4. **Concurrency & Recovery (3 weeks):** Optimistic concurrency control, tombstone vacuum, crash recovery testing.
5. **Integration & Polishing (3 weeks):** DuckDB/Polars/DataFusion connectors, documentation, packaging.

## Appendix: Key References

- Arrow dataset API lacks transaction support; concurrent writes may result in inconsistent data [oai_citation:4‡arrow.apache.org](https://arrow.apache.org/docs/python/dataset.html#:~:text=A%20note%20on%20transactions%20%26,ACID%20guarantees).
- DuckDB’s `COPY … TO` with `RETURN_STATS` returns file names, counts, sizes and column statistics [oai_citation:5‡duckdb.org](https://duckdb.org/docs/stable/sql/statements/copy#:~:text=).
- PyArrow’s `write_dataset` accepts a `file_visitor` callback that yields both file path and metadata [oai_citation:6‡arrow.apache.org](https://arrow.apache.org/docs/python/generated/pyarrow.dataset.write_dataset.html#:~:text=could%20end%20up%20with%20very,small%20row%20groups).
- DuckDB supports unique file naming via `FILENAME_PATTERN 'file_{uuid}'` or `{uuidv7}` patterns [oai_citation:7‡duckdb.org](https://duckdb.org/docs/stable/data/partitioning/partitioned_writes#:~:text=%60FILENAME_PATTERN%60%20a%20pattern%20with%20%60,defined%20to%20create%20specific%20filenames).
