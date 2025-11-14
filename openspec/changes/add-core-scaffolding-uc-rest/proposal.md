## Why
- Establish the foundational Lagoon objects so later phases can plug in table format adapters without reworking base types.
- Provide a typed wrapper around the Unity Catalog Python SDK, enabling consistent metadata retrieval and CRUD by table name.
- Define routing and adapter contracts up front to keep format-specific implementations small and isolated in subsequent phases.

## What Changes
- Introduce `TableMetadata` and `BaseTable` in `src/lagoon/core.py` to model catalog metadata and the table facade interface.
- Add a `UCClient` wrapper in `src/lagoon/client.py` that forwards `get_table`, `list_tables`, `create_table`, and `drop_table` to `unitycatalog-python`, normalizing responses and errors.
- Define a `TableAdapter` `Protocol` in `src/lagoon/adapters/base.py` describing `to_arrow`, `to_polars`, `write`, and `delete` operations.
- Implement `dispatch.build_table` to resolve metadata via `UCClient`, map `data_source_format` to the correct adapter, and raise a precise error for unsupported formats.
- Create tests using `respx` to cover the UC REST wrapper and routing behavior, and configure baseline `ruff`, `mypy`, and `pytest` runs.

## Impact
- Unlocks future adapters (Delta, Parquet, Iceberg) by freezing shared abstractions early.
- Reduces risk of inconsistent Unity Catalog usage by funneling all REST interactions through the typed client.
- No backwards compatibility concerns; the package is pre-1.0 and this proposal introduces the initial public surface.
- Requires adding `unitycatalog-python` (and test-only `respx`) as dependencies; no additional infrastructure changes expected.
