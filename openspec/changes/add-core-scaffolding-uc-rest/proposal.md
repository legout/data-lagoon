## Why
Phase 1 establishes the foundational architecture for data-lagoon, providing the core abstractions, client integration, and routing logic necessary to unify Delta, Iceberg, and Parquet table operations through a single interface. This scaffolding enables the project's vision of format-agnostic table management while ensuring proper type safety and testability from the start.

## What Changes
- Add core table abstraction layer with `TableMetadata` dataclass and `BaseTable` facade
- Implement Unity Catalog client wrapper using the official `unitycatalog-python` SDK
- Define `TableAdapter` Protocol for format-specific implementations
- Create format dispatcher to route operations to appropriate adapters (DELTA, ICEBERG, PARQUET)
- Establish testing infrastructure with proper mocking for Unity Catalog interactions
- Set up code quality standards with ruff, mypy, and pytest

## Impact
- **Affected specs**: All future data-lagoon capabilities will depend on these foundational components
- **Affected code**: Core modules (`core.py`, `client.py`, `dispatch.py`, `adapters/base.py`) and test infrastructure
- **Dependencies**: Adds `unitycatalog-python` as required dependency; establishes testing patterns
- **Breaking changes**: None - this is net-new functionality for the initial scaffold