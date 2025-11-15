## MODIFIED Requirements

### Requirement: Encode Partition Filters as Fragment Partition Expressions
Partition key/value filters SHALL be encoded as fragment partition expressions so that PyArrow can prune entire fragments based on partition values.

#### Scenario: Year partition pruning via fragment expressions
- **WHEN** a dataset is partitioned by `year`
- **AND** a client applies a predicate like `year == '2021'`
- **THEN** the fragments representing files from other years SHALL have partition expressions that conflict with the predicate and be skipped by PyArrow’s pruning
- **AND** only fragments whose partition expressions match the predicate SHALL be scanned.

