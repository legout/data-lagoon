## 1. Core Table Abstraction
- [ ] 1.1 Implement `TableMetadata` dataclass in `src/lagoon/core.py`
- [ ] 1.2 Implement `BaseTable` facade class in `src/lagoon/core.py`
- [ ] 1.3 Add type annotations for all core structures
- [ ] 1.4 Write unit tests for core abstractions in `tests/test_core.py`

## 2. Unity Catalog Client Wrapper
- [ ] 2.1 Implement `UCClient` class in `src/lagoon/client.py`
- [ ] 2.2 Add `get_table(full_name: str) -> dict` method
- [ ] 2.3 Add `list_tables(catalog: str, schema: str) -> list[dict]` method
- [ ] 2.4 Add `create_table(**kwargs) -> dict` method (minimal implementation)
- [ ] 2.5 Add `drop_table(full_name: str) -> None` method
- [ ] 2.6 Write integration tests with `respx` mocking in `tests/test_client.py`

## 3. Table Adapter Protocol
- [ ] 3.1 Define `TableAdapter` Protocol in `src/lagoon/adapters/base.py`
- [ ] 3.2 Specify `to_arrow()` method signature
- [ ] 3.3 Specify `to_polars()` method signature
- [ ] 3.4 Specify `write(df, mode: str) -> None` method signature
- [ ] 3.5 Specify `delete(where: str | None) -> None` method signature
- [ ] 3.6 Write protocol compliance tests in `tests/adapters/test_base.py`

## 4. Format Dispatcher
- [ ] 4.1 Implement `build_table` routing function in `src/lagoon/dispatch.py`
- [ ] 4.2 Add format detection logic for DELTA/ICEBERG/PARQUET
- [ ] 4.3 Implement adapter selection based on table metadata
- [ ] 4.4 Add `UnsupportedFormatError` exception handling
- [ ] 4.5 Write dispatcher tests in `tests/test_dispatch.py`

## 5. Code Quality & Tooling
- [ ] 5.1 Configure `ruff` with appropriate rules
- [ ] 5.2 Configure `mypy` with strict type checking
- [ ] 5.3 Set up `pytest` configuration and fixtures
- [ ] 5.4 Ensure all tests pass with `pytest --cov`
- [ ] 5.5 Verify `ruff check` and `mypy` pass cleanly
- [ ] 5.6 Add pre-commit hooks for code quality

## 6. Documentation & Examples
- [ ] 6.1 Add comprehensive docstrings to all public APIs
- [ ] 6.2 Create usage examples in docstrings
- [ ] 6.3 Update `README.md` with basic usage pattern
- [ ] 6.4 Add type hints examples for IDE support