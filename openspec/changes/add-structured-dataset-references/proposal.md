## Why

The current API accepts dataset references as plain strings and guesses whether they are names or URIs using heuristics. As the project grows—adding more catalog backends, versioned URIs, and richer metadata—it becomes brittle to keep guessing from strings. A structured dataset reference object would allow clients to explicitly specify identifiers (name, base URI, catalog ID, version, optional metadata), enable future URI schemes like `lagoon://<catalog>/<dataset>`, and reduce ambiguity in APIs such as `write_dataset`, `read_dataset`, and catalog utilities.

## What Changes

- Introduce a typed `DatasetRef` structure that can capture:
  - `name` (optional), `base_uri` (optional), `dataset_id` (optional), and `catalog_uri`.
  - Optional `version` and metadata like `tags` or `description`.
  - Methods to convert from existing string inputs and to produce canonical URIs.
- Update the `dataset-core` capability/spec to require APIs to accept structured references and remove ambiguity about how datasets are resolved.
- Provide shims so existing string-based callers continue to work, but internally the system uses `DatasetRef` everywhere.

## Impact

- Affected specs: `dataset-core` (MODIFIED / ADDED sections for structured references).
- Downstream changes (future): `dataset-write`, `dataset-read`, catalog manager, engine helpers, CLI commands.

