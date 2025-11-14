## 1. Implementation
- [ ] 1.1 Define `TableMetadata` dataclass and `BaseTable` facade in `src/lagoon/core.py`.
- [ ] 1.2 Implement `UCClient` with `get_table`, `list_tables`, `create_table`, and `drop_table` using `unitycatalog-python` in `src/lagoon/client.py`.
- [ ] 1.3 Declare the `TableAdapter` `Protocol` (and any shared helpers) in `src/lagoon/adapters/base.py`.
- [ ] 1.4 Add `dispatch.build_table` that resolves metadata via `UCClient`, selects the correct adapter for DELTA/ICEBERG/PARQUET, and errors on unsupported formats.
- [ ] 1.5 Export the new facade entry points from `src/lagoon/__init__.py` for downstream consumers.

## 2. Testing & Tooling
- [ ] 2.1 Add `respx`-backed tests covering `UCClient` happy-path and error translations.
- [ ] 2.2 Add routing tests that validate adapter selection for DELTA, ICEBERG, and PARQUET formats.
- [ ] 2.3 Configure the repo so `ruff check .`, `mypy .`, and `pytest` execute cleanly for the new modules.
