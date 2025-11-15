## ADDED Requirements

### Requirement: Row-Group Indexing in Catalog
The system SHALL maintain a row-group-level index in the `row_groups` table that links each row group to its parent file and captures statistics needed for pruning.

#### Scenario: Create row-groups entries after write
- **WHEN** a write operation completes and file-level metadata has been collected
- **THEN** the system SHALL create one `row_groups` record per physical row group in each Parquet file
- **AND** each record SHALL include `file_id`, `row_group_index`, `row_count`, and serialized per-column `stats_min_json`, `stats_max_json`, and `null_counts_json` fields.

### Requirement: Partition Metadata Storage
The system SHALL store partition information for partitioned datasets in the `partitions` table so that files can be pruned by partition predicates in later capabilities.

#### Scenario: Store partition key/value pairs for file
- **WHEN** a write operation creates a Parquet file under partition directories (e.g., `date=2024-01-01/product=widgets`)
- **THEN** the system SHALL parse partition key/value pairs from the file path or writer-provided metadata
- **AND** it SHALL insert one or more rows into the `partitions` table with `file_id`, `key`, and `value` for each partition component.

### Requirement: Queryability of Statistics by Dataset and Version
Row-group and partition metadata in the catalog SHALL be queryable by dataset and version so that future capabilities can implement predicate pushdown and partition pruning.

#### Scenario: Lookup row-group stats for dataset version
- **WHEN** a client or internal component queries the catalog for a given dataset and version
- **THEN** the system SHALL be able to return all matching `row_groups` records joined to `files`
- **AND** it SHALL be able to filter or aggregate these records based on stored statistics and partition values.

