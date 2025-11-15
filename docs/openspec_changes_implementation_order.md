Recommended order, roughly respecting dependencies and risk:

  1. add-core-dataset-and-catalog (done) – foundation for everything else.
  2. add-structured-dataset-references – clarifies API inputs before more features depend on them.
  3. add-basic-write-and-read-apis – first end-to-end functionality built on the catalog +
     DatasetRef.
  4. add-parquet-storage-layer-and-file-naming – plugs in real storage/UUID naming for the basic
     APIs.
  5. add-statistics-collection-and-rowgroup-index – collect metadata needed for pruning.
  6. add-predicate-and-partition-pruning-reader – uses the collected metadata for performance.
  7. add-schema-evolution-and-enforcement – ensures writes stay compatible as schemas change.
  8. add-transactions-and-concurrency-control – gives multi-writer safety once basic writes work.
  9. add-postgres-catalog-connector – brings Postgres online once the transaction model is in place
     (benefits from advisory locks defined above).
  10. add-vacuum-and-recovery-operations – maintenance tooling once commits/tombstones exist.
  11. add-engine-integrations-and-query-helpers – polish layer that consumes the optimized reader.
  12. add-testing-benchmarking-and-hardening – final reinforcement across all capabilities.

This order keeps the surface area manageable: build core primitives → basic read/write → storage
+ metadata → performance → safety (schema, concurrency, Postgres) → maintenance → integrations
→ global tests/benchmarks. Let me know if you prefer to prioritize Postgres earlier (e.g., right
after schema/concurrency work) for infrastructure reasons.
