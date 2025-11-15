## Context
- Consumes metadata from statistics/partition changes to avoid scanning irrelevant files/row groups.
- Applies to `read_dataset` and future engine helpers.

## Goals
- Define predicate representation (e.g., normalized expression tree or simple list of comparisons).
- Translate predicates into catalog queries that filter `row_groups` and `partitions`.
- Build PyArrow `ParquetFragment`s from pruned file/row-group sets.
- Provide safe fallback when stats/partitions are missing.

## Design Overview

### Predicate Representation
- Use a structured filter format (e.g., list of tuples `(column, op, value)` with `AND` conjunction).
- Accept SQL-style strings as future extension; core implementation works on structured form.
- Add helper `PredicateSet` to normalize inputs.

### Catalog Query Flow
1. Resolve dataset + version.
2. Query `partitions` table to prune files by partition values (if predicate includes partition columns).
3. Query `row_groups` joined with `files` to prune by min/max statistics.
4. Merge results to obtain `(file_path, row_group_indexes)` list.

### Dataset Construction
- Use PyArrow Dataset API:
  ```python
  fragments = [
      ds.ParquetFileFragment(path, filesystem=fs, row_groups=row_group_indices, partition_expression=...)
  ]
  dataset = ds.FileSystemDataset.from_fragments(schema, fragments)
  ```
- Attach filter expressions so downstream engines can reuse them.

### Fallback Logic
- If predicate references columns without stats/partitions → include all files/row groups.
- Always ensure results are a superset of true matches (no false negatives).

## Key Decisions
- Keep predicate format simple initially; can expand to more complex boolean expressions later.
- Perform pruning at the catalog level to minimize storage reads before touching PyArrow.
- Return pruned dataset even if user intends to materialize via DuckDB/Polars.

## Risks
- Catalog queries may become heavy for large datasets → add indexes as needed (already in spec).
- Complex predicates (OR, nested expressions) not supported initially → document limitation.

## Open Questions
- Should we surface diagnostics (e.g., number of files skipped) to users?
- How to integrate with future partition filters in storage layer (e.g., Hive-style directories)? Likely reuse same partition metadata.
