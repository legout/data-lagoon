## MODIFIED Requirements

### Requirement: Support Partitioned Writes
`write_dataset` SHALL allow callers to specify partition columns (e.g., `partition_by=["date", "region"]`) and MUST create Hive-style partition directories under the dataset base path when partitioning is requested.

#### Scenario: Write partitioned dataset
- **WHEN** a client calls `write_dataset(..., partition_by=["date", "region"])`
- **THEN** the system SHALL write Parquet files under `<base>/vX/date=<value>/region=<value>/...`
- **AND** it SHALL capture and persist the partition key/value pairs for each file in the catalog.
