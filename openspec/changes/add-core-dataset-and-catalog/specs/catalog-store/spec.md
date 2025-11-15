## ADDED Requirements

### Requirement: Catalog Tables
The system SHALL maintain a relational metadata catalog with, at minimum, the following logical tables:
- `datasets` (`id`, `name`, `base_uri`, `current_version`, `created_at`)
- `schema_versions` (`id`, `dataset_id`, `version`, `arrow_schema`, `created_at`)
- `transactions` (`id`, `dataset_id`, `version`, `timestamp`, `operation`, `metadata_json`)
- `files` (`id`, `dataset_id`, `version`, `file_path`, `file_size_bytes`, `row_count`, `created_at`, `is_tombstoned`)
- `row_groups` (`id`, `file_id`, `row_group_index`, `stats_min_json`, `stats_max_json`, `null_counts_json`, `row_count`)
- `partitions` (`file_id`, `key`, `value`)

These tables MAY be implemented with different concrete DDL across backends (DuckDB, SQLite, PostgreSQL) but MUST preserve the logical fields and relationships.

#### Scenario: Initialize catalog schema
- **WHEN** the library is configured with a new or empty metadata database
- **THEN** it SHALL create the catalog tables defined above
- **AND** it SHALL be able to query them immediately after creation.

### Requirement: Initial Schema Version Storage
When a dataset is first created, the system SHALL be able to store its initial logical schema as an Arrow schema representation in the catalog.

#### Scenario: Store initial schema for new dataset
- **WHEN** a client registers a new dataset and supplies a schema
- **THEN** the system SHALL insert a `schema_versions` row with `version = 0`
- **AND** it SHALL associate that row with the dataset’s identifier.

### Requirement: Dataset Version Tracking (High-Level)
The catalog SHALL maintain a `current_version` field on each dataset and version numbers in the `transactions` table, but this change does NOT yet define full transaction semantics or concurrency control.

#### Scenario: Update dataset current_version
- **WHEN** a new version is recorded for a dataset (e.g., after a successful write in later changes)
- **THEN** the system SHALL update the dataset’s `current_version` to that version number
- **AND** it SHALL be possible to query the catalog for the latest version of that dataset.

