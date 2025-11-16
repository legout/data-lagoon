## 1. Implementation

- [x] 1.1 Extend connection factory to parse `postgresql://` URIs and create psycopg connection pools
- [x] 1.2 Define Postgres-specific schema DDL (types, indexes, sequences) and migrations
- [x] 1.3 Implement advisory-lock helpers for dataset-level commit locking
- [x] 1.4 Ensure Arrow schema blobs and metadata JSON are stored using `bytea` + `jsonb`
- [x] 1.5 Add integration tests that run against a Postgres instance and validate catalog operations
