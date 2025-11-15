## Why

The project needs foundational, well-specified concepts for datasets and the metadata catalog before higher-level features (statistics, pruning, schema evolution, transactions) can be implemented. Today, there is no canonical way to register a dataset, resolve its storage location, or persist basic metadata about versions and files. This change introduces the minimum viable “table” abstraction and catalog schema so subsequent changes can build on a stable core.

## What Changes

- Define a `dataset-core` capability for identifying datasets by `name` and `base_uri`, and for resolving dataset URIs.
- Define a `catalog-store` capability that specifies relational tables for datasets, schema versions, transactions, files, row groups, and partitions.
- Specify how initial schemas are stored when a dataset is first created/registered.
- Specify how dataset versions are tracked at a high level (version field, created_at) without yet defining full transaction semantics.
- Provide requirements for portability across DuckDB, SQLite, and PostgreSQL as catalog backends.

## Impact

- Affected specs: `dataset-core`, `catalog-store`.
- Affected code (future implementation):
  - Core dataset model (e.g., `data_lagoon.dataset`).
  - Catalog abstraction and DB schema management (e.g., `data_lagoon.catalog`).
  - Any future read/write APIs will depend on these capabilities for dataset lookup and metadata persistence.

