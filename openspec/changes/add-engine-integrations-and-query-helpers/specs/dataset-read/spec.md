## MODIFIED Requirements

### Requirement: Engine-Friendly Dataset Representation
`read_dataset` SHALL return an Arrow-compatible dataset or table representation that can be passed directly to engine integration helpers without additional copying or format conversion.

#### Scenario: Pass dataset to engine helper
- **WHEN** a client calls `read_dataset` and obtains a dataset handle
- **AND** then passes that handle to an engine-specific helper (DuckDB, Polars, DataFusion)
- **THEN** the helper SHALL be able to consume this handle without rewriting data on disk
- **AND** it SHALL construct an engine-native object that reflects the same snapshot and pruning semantics.

### Requirement: Optional Convenience Wrappers for Engine Objects
If the system provides convenience wrappers or methods on the dataset object (e.g., `to_duckdb()`, `to_polars()`), they SHALL internally delegate to the engine integration helpers while preserving all pruning and snapshot guarantees.

#### Scenario: Use convenience wrapper to create engine object
- **WHEN** a dataset object exposes a `to_duckdb()` or similar method
- **THEN** calling that method SHALL internally reuse the same pruning-aware selection logic and integration helper
- **AND** it SHALL return an engine-native object equivalent to using the helper directly.
