## Why
Establish the foundational data structures and Unity Catalog integration for the data-lagoon Python SDK. This core scaffolding enables users to discover, read, write, and manage tables across Delta, Iceberg, and Parquet formats through a unified interface, while using the official `unitycatalog-python` SDK for all metadata operations.

## What Changes
- Add core data models (`TableMetadata`, `BaseTable`) for unified table representation
- Add UC client wrapper using `unitycatalog-python` for catalog operations
- Add `TableAdapter` protocol defining interface for format-specific implementations
- Add dispatcher that routes table operations based on format type (DELTA/ICEBERG/PARQUET)
- Create comprehensive test suite with mocked UC client using `respx`
- Ensure full type coverage and linting compliance

## Impact
- **New Capabilities**: Core SDK foundation, UC integration, format routing
- **Affected specs**: core-data-models, uc-client, adapter-protocol, dispatcher
- **Affected code**: New files in `src/lagoon/` including `core.py`, `client.py`, `dispatch.py`, and `adapters/base.py`
- **Breaking Changes**: None - this is foundational scaffolding that doesn't modify existing APIs
- **Dependencies**: unitycatalog-python, pytest, respx, typing-extensions
