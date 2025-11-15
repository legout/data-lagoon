## MODIFIED Requirements

### Requirement: Snapshot Reads by Version
`read_dataset` SHALL always use a snapshot version of the dataset, either specified explicitly or resolved as the current version at the start of the read.

#### Scenario: Read latest version during concurrent writes
- **WHEN** a client calls `read_dataset` with no explicit version while another writer is in the process of committing
- **THEN** the system SHALL determine the dataset’s `current_version` at the start of the read
- **AND** it SHALL read only the files associated with that version
- **AND** it SHALL NOT expose any partial state from the in-flight commit.

### Requirement: Stable Historical Reads
When a specific version is requested, `read_dataset` SHALL return a consistent snapshot corresponding exactly to that version even if newer versions have been created.

#### Scenario: Read older version after multiple commits
- **WHEN** a client calls `read_dataset` with a dataset reference and `version = N`
- **AND** newer versions `N+1`, `N+2`, … exist in the catalog
- **THEN** the system SHALL load only files that belong to version `N`
- **AND** it SHALL ignore any files or catalog entries associated with later versions.

