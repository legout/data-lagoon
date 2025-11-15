## ADDED Requirements

### Requirement: Partition-Based File Pruning
The system SHALL use partition key/value metadata to exclude entire files from reads when their partition values cannot satisfy the caller’s predicates.

#### Scenario: Date partition pruning
- **WHEN** a dataset is partitioned by `date`
- **AND** a client calls `read_dataset` with a predicate restricting `date` to a specific range
- **THEN** the system SHALL use the `partitions` table to select only files whose `date` partition values overlap the requested range
- **AND** files whose partition values fall completely outside the range SHALL be excluded from the dataset construction.

### Requirement: Combine Partition and Statistics Pruning
The system SHALL combine partition-based pruning and statistics-based pruning so that files and row groups are filtered as early and aggressively as possible without affecting correctness.

#### Scenario: Combined partition and statistics pruning
- **WHEN** a dataset is partitioned by `date` and has row-group statistics for `product_id`
- **AND** a client calls `read_dataset` with predicates on both `date` and `product_id`
- **THEN** the system SHALL first use partition metadata to restrict candidate files by `date`
- **AND** it SHALL then apply row-group statistics on `product_id` within those files to further prune row groups
- **AND** the resulting dataset SHALL only include row groups that may satisfy both predicates.

### Requirement: Support Non-Partitioned Datasets
For datasets without explicit partition directories, the absence of partition metadata SHALL NOT prevent the use of statistics-based pruning.

#### Scenario: Non-partitioned dataset with statistics
- **WHEN** a dataset has no partition key/value entries in the `partitions` table
- **AND** a client calls `read_dataset` with predicates that can be applied using row-group statistics
- **THEN** the system SHALL still apply statistics-based pruning over `row_groups`
- **AND** it SHALL treat the absence of partitions as “no partition-based pruning available” rather than a failure.

