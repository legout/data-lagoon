# Change Proposal: Add Core Infrastructure

## Why
data-lagoon needs foundational type definitions, client abstractions, and routing logic to enable format-agnostic table operations across Delta, Iceberg, and Parquet formats. This establishes the core architecture that subsequent phases will build upon.

## What Changes
- Add core type system (`TableMetadata`, `BaseTable`) for unified table representation
- Implement UC client wrapper using `unitycatalog-python` SDK
- Define `TableAdapter` protocol for format-agnostic operations
- Create format dispatcher to route operations based on table metadata
- Establish testing infrastructure with mocked UC client

## Impact
- **Affected specs**: New `core` capability specification
- **Affected code**: 
  - `src/lagoon/core.py` - type definitions
  - `src/lagoon/client.py` - UC client wrapper  
  - `src/lagoon/dispatch.py` - routing logic
  - `src/lagoon/adapters/base.py` - adapter protocol
  - `tests/` - comprehensive test suite
- **Dependencies**: Adds `unitycatalog-python`, `respx` for testing

This change enables the fundamental architecture pattern where users interact with tables by name (`catalog.schema.table`) while Lagoon handles format-specific routing automatically.
