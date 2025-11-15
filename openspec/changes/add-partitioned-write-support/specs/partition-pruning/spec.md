## MODIFIED Requirements

### Requirement: Partition Metadata Availability
Partition pruning logic SHALL be able to rely on catalog-stored partition key/value pairs because `write_dataset` records them for every file written with partitioning.

#### Scenario: Prune partitions based on catalog metadata
- **WHEN** `read_dataset` receives a predicate on a partition column (e.g., `date = '2024-01-01'`)
- **THEN** it SHALL query the catalog `partitions` table (populated during write) to select only the matching partition directories without scanning storage.
