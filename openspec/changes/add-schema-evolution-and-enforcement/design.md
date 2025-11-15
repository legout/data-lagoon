## Context
- Builds on basic writes to enforce schema consistency and support additive schema evolution.
- Introduces schema merging and type promotion logic described in the spec.

## Goals
- Persist Arrow schemas in `schema_versions` and track which schema each file uses.
- Compare incoming data schema with current catalog schema before each write.
- Provide configurable merge strategy (enable/disable, promotion rules, fallback to string).
- Surface meaningful errors when schemas are incompatible.

## Non-Goals
- Column-level ACLs or advanced data model migrations.
- Full ALTER TABLE operations; this is limited to appending with schema changes.

## Design Overview

### Schema Storage
- Serialize Arrow schema using `pyarrow.ipc.serialize_schema` to bytes.
- When dataset created, version 0 stored.
- Each write stores schema version ID on file records.

### Merge Algorithm
1. Load current schema from catalog.
2. Compare field-by-field:
   - Missing in new data → allow (NULL fill) when merge enabled.
   - New field → append as nullable column.
   - Type mismatch → consult promotion table (e.g., `int32→int64`, `int->decimal`). If no rule, optionally promote to `string`.
3. If merge disabled or no promotion rule, raise `SchemaMismatchError`.

### Configuration
- `write_dataset(..., schema_merge=True, promote_to_string=True/False)`.
- Persist merge policy per dataset in catalog metadata (optional).

### Implementation Notes
- Schema manager component:
  ```python
  class SchemaManager:
      def read_current(dataset_id) -> ArrowSchema
      def merge(incoming: ArrowSchema, current: ArrowSchema, options) -> MergeResult
  ```
- `MergeResult` contains merged schema + list of changes (for logging).

## Risks
- Arrow schema serialization compatibility across versions → rely on PyArrow’s stable IPC format.
- Type promotion can hide data issues → make options explicit and default conservative.

## Open Questions
- Should we allow dropping columns (probably no for now)?
- How to handle metadata (field metadata dict) differences? For now, prefer incoming metadata.
