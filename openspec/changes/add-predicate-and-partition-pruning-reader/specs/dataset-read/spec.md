## MODIFIED Requirements

### Requirement: Pruning-Aware Reads With Predicates
The `read_dataset` API SHALL use catalog statistics and partition metadata, when available, to avoid scanning files and row groups that cannot satisfy the caller’s predicates, while preserving snapshot semantics.

#### Scenario: Apply predicate with statistics and partition pruning
- **WHEN** a client calls `read_dataset` with a dataset reference, a version, and a filter predicate over one or more columns
- **AND** the catalog contains row-group statistics and partition metadata for that dataset and version
- **THEN** the system SHALL select only those files and row groups whose statistics and partition values indicate they may contain matching rows
- **AND** it SHALL construct the underlying dataset (e.g., PyArrow `FileSystemDataset`) using only the selected files and row groups
- **AND** it SHALL return results equivalent to scanning all files and row groups for that version and applying the same predicate.

### Requirement: Correctness Over Aggressiveness
When statistics or partition metadata are unavailable, incomplete, or unsupported for a column type, the reader SHALL favor correctness over aggressiveness by including more files or row groups instead of risking data loss.

#### Scenario: Missing statistics causes conservative fallback
- **WHEN** a client calls `read_dataset` with predicates on a column that lacks reliable statistics in the catalog
- **THEN** the system MAY skip pruning on that column
- **AND** it SHALL include all files and row groups that might contain matching data, even if that results in scanning more data than strictly necessary
- **AND** the returned results SHALL remain correct relative to the full dataset.

