## ADDED Requirements

### Requirement: Dataset Identity
The system SHALL represent each dataset with a stable identity that includes at least:
- A human-readable `name`.
- A `base_uri` pointing to the root storage location (e.g., `file:///data/lake/sales`, `s3://bucket/path`).

#### Scenario: Create new dataset identity
- **WHEN** a client creates or registers a dataset with a `name` and `base_uri`
- **THEN** the system SHALL persist that identity in the catalog
- **AND** it SHALL return a dataset identifier that can be used in future operations.

### Requirement: Dataset URI Resolution
The system SHALL support resolving a dataset reference (dataset name or full URI) into a concrete `base_uri` and catalog entry.

#### Scenario: Resolve dataset by name
- **WHEN** a client calls the API with a dataset `name`
- **THEN** the system SHALL look up the dataset in the catalog
- **AND** it SHALL return the associated `base_uri` and dataset identifier.

#### Scenario: Resolve dataset by URI
- **WHEN** a client passes a `dataset_uri` that fully specifies the storage location
- **THEN** the system SHALL either:
  - Resolve it to an existing catalog entry if one exists, or
  - Treat it as a new dataset candidate that can be registered explicitly.

### Requirement: Dataset Creation and Idempotency
The system SHALL provide an operation to create or register a dataset in the catalog and MUST behave idempotently when called with the same `name` and `base_uri`.

#### Scenario: Create dataset once
- **WHEN** a client calls “create dataset” with a new `name` and `base_uri`
- **THEN** the system SHALL insert a new dataset row
- **AND** it SHALL return the created dataset identifier.

#### Scenario: Re-create existing dataset
- **WHEN** a client calls “create dataset” again with the same `name` and `base_uri`
- **THEN** the system SHALL NOT create a duplicate dataset
- **AND** it SHALL return the existing dataset identifier.

