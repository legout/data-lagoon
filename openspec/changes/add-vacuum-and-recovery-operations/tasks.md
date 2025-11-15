## 1. Implementation

- [ ] 1.1 Implement a `vacuum` API that identifies tombstoned and unreferenced files
- [ ] 1.2 Apply retention policies before deleting files from storage
- [ ] 1.3 Implement startup or on-demand recovery that reconciles catalog and storage
- [ ] 1.4 Ensure recovery marks stray files as tombstones and cleans up incomplete catalog rows when safe
- [ ] 1.5 Add logging/metrics around vacuum and recovery actions
- [ ] 1.6 Add tests simulating crashes and verifying cleanup behavior

