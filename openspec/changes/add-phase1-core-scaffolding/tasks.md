## 1. Core scaffolding
- [ ] 1.1 Implement TableMetadata dataclass and BaseTable abstraction.
- [ ] 1.2 Implement UCClient with `get_table`, `list_tables`, `create_table`, and `drop_table` using `unitycatalog-python`.
- [ ] 1.3 Implement `dispatch.build_table` to select adapters for DELTA, ICEBERG, and PARQUET formats and fail fast on unsupported formats.
- [ ] 1.4 Add unit tests covering UCClient (with `respx`) and dispatch routing behavior.
- [ ] 1.5 Ensure `ruff`, `mypy`, and `pytest` pass.
- [ ] 1.6 Run `openspec validate add-phase1-core-scaffolding --strict`.
