## Why
Phase 1 of the PRD requires foundational scaffolding so Lagoon can represent Unity Catalog tables, wrap the official SDK, and prepare adapter dispatching.

## What Changes
- Introduce TableMetadata dataclass and BaseTable facade as core primitives.
- Implement UCClient wrapper with get/list/create/drop operations that delegate to `unitycatalog-python`.
- Add dispatch factory that maps Unity Catalog formats (DELTA, ICEBERG, PARQUET) to adapter constructors, with unsupported-format guards.
- Establish accompanying unit tests and ensure linting/type checking/test suites remain green.

## Impact
- Affected specs: `core-foundation`
- Affected code: `src/lagoon/core.py`, `src/lagoon/client.py`, `src/lagoon/dispatch.py`, `tests/`
