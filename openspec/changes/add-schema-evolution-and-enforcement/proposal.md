## Why

Users need to evolve dataset schemas over time (e.g., add new columns or adjust types) without rewriting historical data, while still catching incompatible changes early. The current specs define how schemas are stored and how data is written, but they do not yet specify consistent rules for schema merging, type promotion, or strict enforcement. This change introduces a dedicated schema management capability and ties `write_dataset` to clear, configurable schema evolution behavior aligned with the PRD and technical spec.

## What Changes

- Introduce a `schema-management` capability that:
  - Defines how the current schema for a dataset is loaded from the catalog and represented as an Arrow schema.
  - Specifies schema versioning behavior: each schema change produces a new `schema_versions.version` and files record which schema version they adhere to.
  - Defines schema merge behavior when `schema_merge=True` and a set of type promotion rules (e.g., `int32` → `int64`, numeric → `decimal`, fallback to `string/utf8` when allowed).
  - Defines strict enforcement behavior when merging is disabled or promotion is not permitted (raise a `SchemaMismatchError` or equivalent).
- Modify the `dataset-write` capability so that:
  - Each write validates the incoming schema against the catalog schema for the dataset.
  - When schema merging is enabled, compatible changes (such as adding columns) are applied and recorded as new schema versions.
  - When schema merging is disabled, any schema differences cause the write to fail before data files are committed.

## Impact

- Affected specs:
  - `schema-management` (new)
  - `dataset-write` (MODIFIED)
- Builds on existing specs:
  - `catalog-store` (`schema_versions` and file ↔ schema links)
  - `dataset-write` (basic write behavior)
- Affected code (future implementation):
  - Schema manager component that compares and merges Arrow schemas.
  - Write path integration that calls the schema manager before writing and updates `schema_versions` and file metadata.

