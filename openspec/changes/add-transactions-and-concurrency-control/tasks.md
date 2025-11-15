## 1. Implementation

- [ ] 1.1 Implement transaction manager for version allocation and conflict detection
- [ ] 1.2 Implement database transaction boundaries and locking per backend
- [ ] 1.3 Integrate transaction manager into `write_dataset` (atomic catalog updates)
- [ ] 1.4 Ensure `read_dataset` uses stable versions and remains isolated from in-flight writes
- [ ] 1.5 Add tests for concurrent writers, conflicts, and crash behavior

