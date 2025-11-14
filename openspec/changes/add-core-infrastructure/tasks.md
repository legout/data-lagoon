# Implementation Tasks: Core Infrastructure

## 1. Core Type System
- [ ] 1.1 Create `src/lagoon/core.py` with `TableMetadata` dataclass
- [ ] 1.2 Implement `BaseTable` facade class with to_arrow/to_polars methods
- [ ] 1.3 Add type hints for Python 3.10+ compatibility
- [ ] 1.4 Write unit tests for core types

## 2. UC Client Wrapper  
- [ ] 2.1 Create `src/lagoon/client.py` with `UCClient` class
- [ ] 2.2 Implement `get_table(full_name)` method using unitycatalog-python
- [ ] 2.3 Implement `list_tables(catalog, schema)` method
- [ ] 2.4 Implement `create_table()` and `drop_table()` methods
- [ ] 2.5 Add error handling for UnityCatalog exceptions
- [ ] 2.6 Write tests with mocked UC client using respx

## 3. Table Adapter Protocol
- [ ] 3.1 Create `src/lagoon/adapters/base.py` with `TableAdapter` protocol
- [ ] 3.2 Define standard adapter interface (to_arrow, to_polars, write, delete)
- [ ] 3.3 Add type signatures for all adapter methods
- [ ] 3.4 Write protocol compliance tests

## 4. Format Dispatcher
- [ ] 4.1 Create `src/lagoon/dispatch.py` with routing logic
- [ ] 4.2 Implement `build_table()` function to route based on format
- [ ] 4.3 Add support for DELTA, ICEBERG, PARQUET format detection
- [ ] 4.4 Handle unknown formats with appropriate error
- [ ] 4.5 Write dispatcher tests with various format scenarios

## 5. Package Infrastructure
- [ ] 5.1 Update `pyproject.toml` with required dependencies
- [ ] 5.2 Configure ruff and mypy settings
- [ ] 5.3 Set up pytest configuration
- [ ] 5.4 Create `src/lagoon/__init__.py` with proper exports

## 6. Validation
- [ ] 6.1 Run `ruff check .` - ensure no linting issues
- [ ] 6.2 Run `mypy .` - ensure type checking passes
- [ ] 6.3 Run `pytest` - ensure all tests pass
- [ ] 6.4 Verify integration between components works correctly
