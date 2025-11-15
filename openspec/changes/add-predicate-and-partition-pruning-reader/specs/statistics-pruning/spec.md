## ADDED Requirements

### Requirement: Translate Predicates to Row-Group Filters
The system SHALL translate caller predicates into catalog-level filters over row-group statistics to select candidate row groups for reading.

#### Scenario: Equality predicate on numeric column
- **WHEN** a client calls `read_dataset` with a predicate such as `column = 42`
- **THEN** the system SHALL issue a catalog query over `row_groups` joined with `files` that selects only row groups where `stats_min_json['column'] <= 42` AND `stats_max_json['column'] >= 42`
- **AND** it SHALL use the resulting file and row-group identifiers to construct the underlying dataset.

### Requirement: Range and Multi-Column Predicates
The system SHALL support at least simple range predicates and conjunction of predicates across multiple columns when applying statistics-based pruning.

#### Scenario: Range predicate with conjunction
- **WHEN** a client calls `read_dataset` with a predicate such as `date >= '2024-01-01' AND date < '2024-02-01' AND product_id = 123`
- **THEN** the system SHALL translate this into catalog filters that:
  - Restrict row groups to those where the stored `date` min/max overlaps the requested date range
  - AND the `product_id` min/max overlaps 123
- **AND** only those row groups SHALL be selected for inclusion in the dataset.

### Requirement: Attach Filters to Fragments
When constructing the underlying dataset from pruned results, the system SHALL attach appropriate filters or partition expressions to each fragment so that downstream engines can apply remaining filtering efficiently.

#### Scenario: Build PyArrow fragments with filters
- **WHEN** the system has determined a set of files and row groups to read based on catalog statistics
- **THEN** it SHALL construct PyArrow `ParquetFragment`s (or equivalent) for each selected file
- **AND** it SHALL attach a filter or `partition_expression` that encodes the caller’s predicate
- **AND** it SHALL build a `FileSystemDataset` from these fragments for use by downstream engines.

