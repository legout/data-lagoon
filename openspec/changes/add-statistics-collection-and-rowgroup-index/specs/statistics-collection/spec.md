## ADDED Requirements

### Requirement: Collect Statistics From DuckDB Writes
When DuckDB is used as the write engine, the system SHALL collect file-level and column-level statistics using the `RETURN_STATS` option of the `COPY` command and persist them in the catalog.

#### Scenario: DuckDB write with RETURN_STATS
- **WHEN** the system writes a dataset using a DuckDB `COPY (SELECT ...) TO <base_dir> (FORMAT parquet, RETURN_STATS)`
- **THEN** it SHALL read the returned result set containing `filename`, `row_count`, `file_size_bytes`, and `column_statistics`
- **AND** it SHALL insert or update entries in the `files` table with at least `file_path`, `file_size_bytes`, `row_count`, and `dataset_id`/`version`
- **AND** it SHALL derive per-row-group and per-column statistics from the `column_statistics` payload and persist them in the `row_groups` table.

### Requirement: Collect Statistics From PyArrow Writes
When PyArrow is used as the write engine, the system SHALL use the `file_visitor` callback to collect file and row-group statistics from `parquet.FileMetaData` and persist them in the catalog.

#### Scenario: PyArrow write with file_visitor
- **WHEN** the system writes a dataset using `pyarrow.dataset.write_dataset` with a `file_visitor` callback
- **THEN** for each `WrittenFile` passed to the callback it SHALL inspect `WrittenFile.path` and `WrittenFile.metadata` (`parquet.FileMetaData`)
- **AND** it SHALL populate the `files` table with `file_path`, `file_size_bytes` (if available), `row_count`, and `dataset_id`/`version`
- **AND** it SHALL iterate over row groups and columns in `FileMetaData` to extract `min`, `max`, and `null_count` values where present
- **AND** it SHALL store these per-row-group statistics in the `row_groups` table.

### Requirement: Handle Missing or Partial Statistics Gracefully
The system SHALL handle cases where some statistics are missing (e.g., due to writer configuration or unsupported types) by recording `NULL` or equivalent placeholders rather than failing the write.

#### Scenario: Missing statistics for some columns
- **WHEN** a writer produces Parquet metadata where some columns or row groups lack `min`, `max`, or `null_count` values
- **THEN** the system SHALL still record a `row_groups` entry for that row group
- **AND** it SHALL set missing statistics fields to `NULL` or an equivalent representation
- **AND** it SHALL NOT fail the write solely due to missing statistics.

