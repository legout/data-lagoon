## MODIFIED Requirements

### Requirement: Structured Dataset References
All public APIs that accept a dataset input SHALL support a structured dataset reference object (`DatasetRef`) that captures at least `name`, `base_uri`, `dataset_id` (optional), and the catalog endpoint.

#### Scenario: Construct dataset ref from name
- **WHEN** a client has only the dataset `name` and catalog endpoint
- **THEN** it SHALL create a `DatasetRef` with the name and catalog info
- **AND** resolution SHALL fill `dataset_id`/`base_uri` once it is looked up in the catalog.

#### Scenario: Construct dataset ref from URI
- **WHEN** a client provides a full dataset URI such as `lagoon://catalog/main/datasets/sales`
- **THEN** it SHALL be parsed into a `DatasetRef` with explicit fields
- **AND** APIs SHALL use those fields without heuristics.

### Requirement: Backward Compatibility for String Inputs
The system SHALL continue to accept string references (names or URIs) for backwards compatibility but MUST convert them into structured references internally before proceeding.

#### Scenario: Legacy string name input
- **WHEN** a client calls `write_dataset("sales", data)`
- **THEN** the API SHALL wrap `"sales"` into a `DatasetRef`
- **AND** all subsequent operations SHALL use the structured reference
- **AND** the behavior SHALL match what would happen if the user passed an equivalent `DatasetRef`.

### Requirement: Canonical Dataset URIs
`DatasetRef` SHALL be able to produce a canonical dataset URI (e.g., `lagoon://<catalog>/<dataset>` or `dataset:<id>`) that uniquely identifies the dataset across catalogs/backends.

#### Scenario: Convert reference to canonical URI
- **WHEN** a client obtains a `DatasetRef` after resolving a dataset
- **THEN** calling `ref.to_uri()` (or equivalent) SHALL return a canonical URI string that can be persisted or shared
- **AND** re-parsing that URI SHALL reproduce the same dataset reference fields.
