## ADDED Requirements
### Requirement: Table metadata representation
Lagoon core SHALL expose a `TableMetadata` dataclass that records the Unity Catalog table name (`catalog.schema.table`), the catalog-reported format (`DELTA`, `ICEBERG`, or `PARQUET`), the resolved storage location, and optional schema JSON details.

#### Scenario: Resolve metadata for Unity Catalog table
- **WHEN** Lagoon retrieves metadata for a Unity Catalog table via `UCClient.get_table`
- **THEN** the resulting `TableMetadata` SHALL contain the canonical table name
- **AND** the `data_source_format` SHALL match the Unity Catalog format string in uppercase
- **AND** the `storage_location` SHALL reflect the path returned by Unity Catalog

### Requirement: BaseTable abstraction
Lagoon core SHALL provide a `BaseTable` facade exposing `to_arrow()`, `to_polars()`, `write(...)`, and `delete(...)` methods that delegate to the active format adapter while raising a descriptive error if the adapter lacks an implementation.

#### Scenario: Delegating to format adapter
- **WHEN** a Delta adapter is constructed via the dispatcher and a consumer calls `BaseTable.to_arrow()`
- **THEN** the call SHALL invoke the adapter’s Arrow reader
- **AND** it SHALL return a `pyarrow.Table`
- **AND** missing adapter functionality SHALL raise `NotImplementedError` with the adapter name

### Requirement: Unity Catalog client operations
Lagoon core SHALL expose a `UCClient` wrapper that delegates `get_table`, `list_tables`, `create_table`, and `drop_table` to the official `unitycatalog-python` SDK while translating SDK errors into Lagoon catalog exceptions.

#### Scenario: Propagating SDK failure
- **WHEN** `UCClient.create_table` invokes the SDK and the SDK raises a `UnityCatalogError`
- **THEN** the wrapper SHALL raise a Lagoon `CatalogError` containing the original message

### Requirement: Format dispatch factory
Lagoon core SHALL provide `dispatch.build_table(metadata, adapters)` that selects the adapter matching `metadata.data_source_format` (Delta, Iceberg, Parquet) and raises `UnsupportedFormatError` for unknown formats.

#### Scenario: Unsupported format guard
- **WHEN** `dispatch.build_table` receives metadata for a `CSV` table without a registered adapter
- **THEN** it SHALL raise `UnsupportedFormatError`
- **AND** the error SHALL state the received format and the supported formats list

### Requirement: Phase 1 scaffolding quality gates
Lagoon Phase 1 scaffolding SHALL run `ruff`, `mypy`, and `pytest` as part of the deliverable to confirm that the new core components are linted, typed, and tested.

#### Scenario: Quality gate enforcement
- **WHEN** the Phase 1 work is executed
- **THEN** running `ruff check .`, `mypy .`, and `pytest` SHALL succeed without errors
