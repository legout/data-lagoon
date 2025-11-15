## MODIFIED Requirements

### Requirement: Use FileSystemDataset and ParquetFragments for Reads
`read_dataset` SHALL construct a `pyarrow.dataset.FileSystemDataset` from a set of `ParquetFragment`s as the primary representation for all reads.

#### Scenario: Build dataset from pruned fragments
- **WHEN** a client calls `read_dataset` with optional predicates
- **THEN** the system SHALL:
  - Resolve the set of candidate files and row groups from the catalog.
  - Construct `ParquetFragment`s for those candidates.
  - Build a `FileSystemDataset` from those fragments and the appropriate filesystem.
- **AND** the dataset SHALL be the basis for both `as_dataset=True` returns and table materialization.

### Requirement: Materialize via Dataset to_table
`read_dataset` SHALL materialize data using `FileSystemDataset.to_table(filter=...)` instead of reading Parquet files directly.

#### Scenario: Filtered read via dataset API
- **WHEN** predicates are provided
- **THEN** the system SHALL convert them into an Arrow `Expression`
- **AND** it SHALL call `dataset.to_table(filter=expression)` to materialize the result.

