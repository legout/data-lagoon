## 1. Implementation

- [ ] 1.1 Review current `dataset-write`/`dataset-read` implementation and identify direct Parquet usage.
- [ ] 1.2 Introduce helper to configure `pyarrow.dataset.write_dataset` (format options, file visitors).
- [ ] 1.3 Capture file metadata via file visitor and persist through catalog helper.
- [ ] 1.4 Update `read_dataset` to construct a `pyarrow.dataset.Dataset` from catalog file list (with optional materialization to `Table`).
- [ ] 1.5 Ensure backward-compatible return types (still allow `pa.Table`) and update tests accordingly.
- [ ] 1.6 Update documentation/spec references and rerun unit tests.
