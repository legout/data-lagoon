## 1. Core Data Models Implementation
- [ ] 1.1 Create `TableMetadata` dataclass with full_name, data_source_format, storage_location properties
- [ ] 1.2 Create `BaseTable` abstract class with to_arrow, to_polars, write, delete methods
- [ ] 1.3 Add comprehensive type annotations and docstrings
- [ ] 1.4 Write unit tests for data model validation and serialization

## 2. UC Client Integration
- [ ] 2.1 Create `UCClient` class wrapping unitycatalog-python SDK
- [ ] 2.2 Implement get_table, list_tables, create_table, drop_table methods
- [ ] 2.3 Add proper error handling and UnityCatalogException mapping
- [ ] 2.4 Write tests using respx to mock UC API calls
- [ ] 2.5 Add configuration validation for UC URL and authentication

## 3. Adapter Protocol Implementation
- [ ] 3.1 Define `TableAdapter` Protocol with required interface methods
- [ ] 3.2 Create base adapter with common functionality
- [ ] 3.3 Define standard exception hierarchy for adapter operations
- [ ] 3.4 Write tests demonstrating protocol compliance

## 4. Dispatcher Implementation
- [ ] 4.1 Create `build_table` function that routes based on format
- [ ] 4.2 Implement format detection logic (DELTA/ICEBERG/PARQUET)
- [ ] 4.3 Add proper handling of unknown/unsupported formats
- [ ] 4.4 Write integration tests for routing logic
- [ ] 4.5 Test with various TableMetadata configurations

## 5. Project Structure and Configuration
- [ ] 5.1 Create `src/lagoon/` directory structure
- [ ] 5.2 Set up `__init__.py` for proper imports
- [ ] 5.3 Configure ruff and mypy settings
- [ ] 5.4 Set up pytest configuration with respx fixtures

## 6. Quality Assurance
- [ ] 6.1 Ensure all code passes ruff linting
- [ ] 6.2 Ensure all code passes mypy type checking
- [ ] 6.3 Achieve 100% test coverage for new modules
- [ ] 6.4 Add integration validation with sample UC responses
