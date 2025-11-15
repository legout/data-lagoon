## Context
- Provides ACID-style guarantees atop the catalog by introducing a versioned transaction log and optimistic concurrency.
- Necessary before multi-writer deployments or Postgres connector.

## Goals
- Ensure each commit atomically updates catalog tables and advances `current_version`.
- Detect conflicting writers via optimistic concurrency control (compare base version vs current).
- Use backend-appropriate locking (SQLite exclusive transactions, DuckDB exclusive transactions, Postgres advisory locks).
- Define transaction manager interface consumed by `write_dataset`.

## Non-Goals
- Distributed consensus or cross-dataset atomicity.
- Multi-statement user transactions beyond dataset commits.

## Design Overview

### Transaction Manager
```python
class TransactionManager:
    def begin(dataset_id) -> TxContext:
        # obtain lock, read current_version
    def commit(tx_context, file_records, row_group_records, metadata) -> int:
        # write catalog entries and update current_version atomically
    def rollback(tx_context):
        # release locks, rollback DB txn
```

- `TxContext` holds DB connection/transaction and base version.
- Writers pass expected base version (latest they observed). If mismatch, raise `ConcurrencyError`.

### Catalog Updates
- Within DB transaction:
  - Insert row into `transactions` with new version = base_version + 1.
  - Insert file/row_group/partition records.
  - Update `datasets.current_version`.
- On failure, rollback ensures no partial state.

### Locking Strategy
- SQLite/DuckDB: wrap commit in exclusive transaction (no concurrent writes).
- Postgres: use advisory locks keyed by `(dataset_id)`. Acquire before commit, release after.

### API Changes
- `write_dataset(..., base_version=None)` optional argument. If `None`, automatically fetch current version before writing and pass to transaction manager.
- Write result returns new version number.

## Risks
- Deadlocks if locks held too long → keep write operations outside DB transaction; only metadata commit is transactional.
- Clock skew not relevant (version numbers monotonic).

## Open Questions
- Should reads be able to specify “repeatable read” semantics? For now, reads fetch `current_version` at start and operate on that snapshot.
- Should we expose `begin_read_transaction` for long-running readers? Possibly later.
