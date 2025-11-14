## Context
Phase 1 establishes the foundational architecture for data-lagoon, a unified Python SDK for managing Unity Catalog tables across Delta, Iceberg, and Parquet formats. The architecture must support format-agnostic operations while providing type safety and extensibility for future enhancements.

## Goals / Non-Goals
- **Goals**:
  - Provide uniform interface across all table formats
  - Ensure type safety with full mypy compliance
  - Enable easy testing with proper mocking support
  - Create extensible adapter pattern for future formats
  - Maintain Python 3.10+ compatibility
- **Non-Goals**:
  - Performance optimization (focus on correctness first)
  - Advanced query planning (deferred to later phases)
  - Multi-threading or async patterns (synchronous API initially)
  - CLI tools or web interfaces (library-only focus)

## Decisions
- **Decision**: Use `unitycatalog-python` official SDK instead of raw REST calls
  - **Rationale**: Guarantees version compatibility, provides better error handling, reduces maintenance burden
  - **Alternatives considered**: Raw HTTP client, auto-generated OpenAPI client

- **Decision**: Implement Protocol-based adapter pattern
  - **Rationale**: Enables duck typing, makes testing easier, allows future adapter implementations
  - **Alternatives considered**: Abstract base classes, simple function-based adapters

- **Decision**: Use dataclasses for metadata structures
  - **Rationale**: Built-in equality, serialization support, less boilerplate than regular classes
  - **Alternatives considered**: TypedDict, Pydantic models, regular classes

- **Decision**: Centralized dispatcher for format routing
  - **Rationale**: Single point of format logic, easier to maintain, consistent error handling
  - **Alternatives considered**: Adapter self-registration, format-specific client methods

## Risks / Trade-offs
- **Risk**: Unity Catalog API changes could break compatibility
  - **Mitigation**: Pin `unitycatalog-python` version, implement clear error boundaries
- **Risk**: Protocol pattern may be too flexible leading to inconsistent adapters
  - **Mitigation**: Comprehensive protocol documentation, strict testing requirements
- **Trade-off**: Additional abstraction layer adds complexity
  - **Balance**: Complexity justified by long-term maintainability and extensibility
- **Risk**: Mocking Unity Catalog in tests may not match real behavior
  - **Mitigation**: Use `respx` for HTTP interception, integration tests against real UC

## Migration Plan
- No migration needed - this is initial implementation
- Future phases will build upon these foundations without breaking changes
- Protocol-based design allows gradual addition of new adapters

## Open Questions
- Should we implement retry logic for Unity Catalog calls in Phase 1 or defer to Phase 2?
- What level of input validation should we implement in the core facade vs. individual adapters?
- Should we include basic caching for table metadata or keep it stateless initially?