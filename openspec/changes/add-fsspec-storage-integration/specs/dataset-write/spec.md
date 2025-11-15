## MODIFIED Requirements

### Requirement: Accept Filesystem Options in Write API
`write_dataset` SHALL accept filesystem configuration (either via dataset reference or explicit parameters) so callers can pass credentials/options required by remote backends.

#### Scenario: Provide S3 credentials
- **WHEN** a client writes to an S3-backed dataset and provides AWS credentials/config
- **THEN** `write_dataset` SHALL forward those options to the storage abstraction / `fsspec` filesystem
- **AND** the resulting files SHALL be written using that configured filesystem without falling back to local temp paths.
