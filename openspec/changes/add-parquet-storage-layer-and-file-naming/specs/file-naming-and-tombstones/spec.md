## ADDED Requirements

### Requirement: UUID v7-Based File Naming
The system SHALL name Parquet data files using a UUID v7-based pattern to ensure uniqueness and timestamp-aware ordering, consistent with the technical specification.

#### Scenario: Generate file name for new Parquet file
- **WHEN** a write operation creates a new Parquet file for a dataset
- **THEN** the system SHALL generate a file name that includes a UUID v7 component (e.g., `part-<uuidv7>.parquet`)
- **AND** it SHALL ensure that file names do not collide even under repeated writes.

### Requirement: Catalog as Source of Truth for Visible Files
The catalog SHALL be the authoritative source of which files belong to each dataset version; files that exist in storage but are not referenced in the catalog SHALL be treated as tombstones and MUST NOT be returned in reads.

#### Scenario: Unreferenced files are invisible to readers
- **WHEN** a Parquet file exists under a dataset’s `base_uri` but has no corresponding row in the `files` table for the selected version
- **THEN** `read_dataset` SHALL NOT include that file in the dataset it returns
- **AND** the presence of such a file SHALL NOT affect query results.

### Requirement: No Temporary Directories for Atomicity
The system SHALL achieve atomic visibility of data through catalog updates and tombstone semantics rather than by relying on temporary directories or renames in the underlying storage.

#### Scenario: Failed write leaves tombstoned files
- **WHEN** a write operation fails after creating one or more Parquet files but before successfully recording a new version in the catalog
- **THEN** those files SHALL remain in storage as tombstones (unreferenced by any version)
- **AND** they SHALL NOT be visible to readers
- **AND** they MAY be deleted later by vacuum/maintenance operations defined in a subsequent change.

