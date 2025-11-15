## Context

We currently:
- Use the catalog’s `row_groups` and `partitions` tables to decide which files/row groups **might** match predicates.
- Manually read those Parquet files using `pyarrow.parquet.ParquetFile` and stitch together a table.

This is at odds with:
- OpenSpec, which calls for a PyArrow **FileSystemDataset** and **ParquetFragments** as the primary representation.
- Delta Lake’s `DeltaTable.to_pyarrow_dataset()` pattern, where filtering and pruning happen through the dataset API using partition values and statistics from the transaction log. citeturn0search4turn0search5

We want to:
- Treat a pruned dataset as a `FileSystemDataset` constructed from `ParquetFragment`s.
- Express pruning logic as Arrow `Expression`s (`partition_expression` per fragment + global filter), and let PyArrow apply predicate pushdown and row-group skipping.
- Use `dataset.to_table(filter=...)` for materialization, ensuring engines like DuckDB, Polars, and DataFusion can reuse the same dataset object.

## High-Level Design

### 1. Predicate Representation → Arrow Expression

- Keep the external API simple: structured predicates as a list of `(column, op, value)` triples with implicit AND.
- Internally:
  - Map each triple to `ds.field(column) <op> value` (e.g., `ds.field("value") >= 3`).
  - Combine them via `&` to form a single `Expression` for `filter=...`.
- Optionally allow callers to pass a `pyarrow.dataset.Expression` directly; in that case, skip conversion.

### 2. Catalog-Driven Candidate Selection

We keep the catalog-centric pruning as the first stage:

1. **Partition-level candidate files:**
   - Look at equality predicates on partition columns.
   - Use `partitions` table to select the subset of `files` whose partition key/value pairs overlap the predicate.
2. **Row-group–level narrowing:**
   - For the selected files, use `row_groups` stats (`stats_min_json`, `stats_max_json`) to find row groups whose ranges overlap predicate values:
     - For `col == v`: keep row groups where `min <= v <= max`.
     - For `col >= v`: keep row groups where `max >= v`.
     - For `col <= v`: keep row groups where `min <= v`.
   - Result: a mapping `{file_id -> [row_group_indices]}`.

This matches what we already do conceptually, but we will now feed the result into the fragment builder instead of directly reading Parquet files.

### 3. Fragment Builder

**Filesystem:**
- Resolve a `pyarrow.fs.FileSystem` rooted at the dataset base_URI (e.g., via `FSSpecHandler` + `PyFileSystem` or `SubTreeFileSystem`).
- This is analogous to Delta’s pattern of using a `SubTreeFileSystem` rooted at the table path when building a dataset. citeturn0search7

**Fragments:**
- For each candidate file:
  - Compute a path relative to the filesystem root (using our existing storage abstraction).
  - Create a `ParquetFragment` for that path.
  - If we have a non-empty row-group list for that file, attach it via the fragment’s `row_groups` argument (or equivalent factory, depending on the PyArrow version).
  - Build a `partition_expression` that combines:
    - **Hive-style partition values**: equality expressions for directory-derived keys (e.g., `ds.field("date") == "2024-01-01"`).
    - **Column statistics constraints** derived from the catalog (per-column `min`/`max` for the file or row group), expressed as:
      - `ds.field("col") >= min_value` AND `ds.field("col") <= max_value`
    - This mirrors Delta’s pattern of encoding both partition and statistics information into the fragment-level expression, so the dataset engine can prune fragments/row groups without bespoke logic.

The outcome is a list of fragments that “know” both their partition context and (optionally) range constraints derived from row-group stats.

### 4. FileSystemDataset Construction

- Build the dataset as:
  ```python
  dataset = ds.FileSystemDataset.from_fragments(schema, fragments, filesystem=arrow_fs)
  ```
- Schema:
  - Prefer to use the Arrow schema from the most recent `schema_versions` entry for the dataset/version.
  - Fallback to `fragments[0].schema` if needed.

### 5. Materialization

- For `as_dataset=True`:
  - Return the `FileSystemDataset` as-is for downstream engines.
- For `as_dataset=False`:
  - Compute an Arrow `Expression` from the predicates.
  - Call:
    ```python
    table = dataset.to_table(filter=expression)
    ```
  - Because the fragment/partition/range information is embedded in the dataset, PyArrow can:
    - Skip fragments entirely based on `partition_expression`.
    - Skip row groups within a fragment based on encoded range constraints and stored Parquet stats.

### 6. Fallback Behavior

- Missing or incomplete stats:
  - If no usable stats exist for a column, do not encode any range constraints for that column in the fragment.
  - The fragment remains in the dataset but only partition-based pruning applies; filter execution becomes row-level within that fragment.
- No predicates:
  - Build fragments without partition expressions and call `dataset.to_table()` with no filter for a full scan.

## Comparison to Delta Lake

- Delta Lake’s `to_pyarrow_dataset`:
  - Computes the list of active files using the Delta transaction log.
  - Builds a PyArrow Dataset from those files and the appropriate filesystem.
  - Lets predicates applied via `.to_table(filter=condition)` leverage partition values and per-file stats for pruning. citeturn0search4turn0search5
- Our refactored reader:
  - Uses the SQL catalog + statistics (rather than a Delta log) to produce a similar set of candidate fragments and pruning expressions.
  - Produces a Dataset object that behaves very similarly under filtering, enabling efficient predicate pushdown for all consumers.

## Risks / Trade-offs

- The fragment-level `partition_expression` may be coarser than true row-group stats (e.g., using file-level min/max). This is acceptable for now and can be refined later.
- Building many small fragments may add overhead; we can group row groups per file into a single fragment initially and optimize later if needed.
- Some PyArrow APIs (e.g., how to attach `row_groups` and `partition_expression`) may differ by version; the implementation must be careful to use the version-appropriate factories.
