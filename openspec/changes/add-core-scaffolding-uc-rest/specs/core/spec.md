## ADDED Requirements

### Requirement: Table Metadata Model
Lagoon MUST expose a typed `TableMetadata` dataclass that captures a Unity Catalog table’s fully qualified name, storage location, declared format, and optional schema JSON so downstream components can reason about tables without re-parsing raw SDK payloads.

#### Scenario: Return typed metadata
- **GIVEN** the Unity Catalog SDK returns metadata for `catalog.schema.table` including `data_source_format`, `storage_location`, and optional schema information
- **WHEN** `UCClient.get_table("catalog.schema.table")` is called
- **THEN** Lagoon returns a `TableMetadata` instance populated with those attributes and type hints validated by `mypy`.

### Requirement: Unity Catalog REST Client
Lagoon MUST provide a `UCClient` wrapper that delegates table CRUD operations to `unitycatalog-python` while translating `UnityCatalogError` exceptions into Lagoon’s `CatalogError` hierarchy.

#### Scenario: Forward get_table with error translation
- **GIVEN** valid Unity Catalog credentials and a registered table
- **WHEN** `UCClient.get_table` is invoked
- **THEN** the client calls the `unitycatalog-python` SDK, converts the SDK response into `TableMetadata`, and if the SDK raises `UnityCatalogError`, Lagoon raises a `CatalogError` subclass instead of propagating the raw SDK exception.

### Requirement: Adapter Protocol
Lagoon MUST define a `TableAdapter` `Protocol` that every format-specific adapter (Delta, Iceberg, Parquet) implements, ensuring common methods and attributes across engines.

#### Scenario: Adapter contract validation
- **GIVEN** a format-specific adapter implementation
- **WHEN** it is type-checked against `TableAdapter`
- **THEN** it exposes `format`, `storage_location`, and callable `to_arrow()`, `to_polars()`, `write(df, mode="append")`, and `delete(where=None)` signatures without bare `except` blocks.

### Requirement: Format Routing
Lagoon MUST provide `dispatch.build_table` that resolves table metadata via `UCClient`, selects the registered adapter for the metadata’s format (DELTA, ICEBERG, PARQUET), and raises a precise error for unsupported formats.

#### Scenario: Select adapter for known format
- **GIVEN** `TableMetadata` with `data_source_format="DELTA"`
- **WHEN** `dispatch.build_table(metadata, client=uc_client)` is called
- **THEN** Lagoon returns an adapter instance (or factory result) registered for DELTA that satisfies `TableAdapter`, and if the format is unknown, it raises `UnsupportedFormatError`.

### Requirement: Tooling Baseline
Lagoon MUST enforce that linting, typing, and unit tests cover the Phase 1 scaffolding to prevent regressions before adding adapters.

#### Scenario: Baseline checks succeed
- **GIVEN** the Phase 1 modules and accompanying tests
- **WHEN** maintainers run `ruff check .`, `mypy .`, and `pytest`
- **THEN** all three commands exit successfully without suppressing real warnings or errors.
