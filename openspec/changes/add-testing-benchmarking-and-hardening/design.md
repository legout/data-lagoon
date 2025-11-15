## Context
- Ensures the feature set (writes, reads, pruning, schema evolution, transactions, maintenance) has adequate test/benchmark coverage.
- Final stage to harden the system before wider adoption.

## Goals
- Define test matrix (unit/integration/durability) mapped to capabilities.
- Introduce benchmark scripts to compare pruned vs full scans.
- Establish guidelines for future changes to update tests/benchmarks.

## Test Strategy

### Unit Tests
- Schema manager merge/promotion logic (add columns, type widening, strict mode errors).
- Transaction manager conflict detection and version increments.
- Storage abstraction path resolution and UUID naming.
- Statistics collector (parse DuckDB RETURN_STATS, PyArrow metadata).

### Integration Tests
- End-to-end write/read on local filesystem with simple dataset.
- Write with schema changes + read verifying merged schema.
- Write + read with predicates to ensure pruning reduces scanned files.
- Engine helper smoke tests (DuckDB/Polars/DataFusion) gating on optional deps.

### Durability / Failure Tests
- Simulate crash after file write but before catalog commit → ensure files become tombstones, reads ignore them.
- Simulate concurrent writers (one commit, one conflict) to verify optimistic concurrency.
- Vacuum/recovery scenario: leave tombstoned files, run vacuum, ensure deletion per retention policy.

## Benchmark Plan
- Synthetic dataset (e.g., 10M rows partitioned by date/product).
- Measure:
  - Full scan read time vs pruned read time with selective predicate.
  - Bytes read and number of row groups touched.
- Tools: simple Python script invoking `read_dataset` with/without pruning; optional integration with DuckDB/Polars for cross-engine metrics.

## Reporting / Automation
- Integrate with CI (where feasible) for unit/integration tests.
- Durability + benchmark tests may run nightly/manual due to heavier resource needs.
- Document how to run each suite locally (dependencies, environment variables).

## Risks
- Benchmarks require large data; provide smaller default dataset with ability to scale up.
- Some tests need optional dependencies (DuckDB, Postgres, cloud storage); mark as skipped when not available.

## Open Questions
- Should we adopt `pytest` for richer fixtures? If so, plan migration from `unittest`.
- How to capture benchmark results over time (e.g., JSON artifacts, docs)? Consider simple CSV log for now.
