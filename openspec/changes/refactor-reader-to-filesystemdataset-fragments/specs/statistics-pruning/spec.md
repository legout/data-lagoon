## MODIFIED Requirements

### Requirement: Encode Statistics as Fragment Expressions
Row-group statistics from the catalog SHALL be encoded into fragment-level expressions (e.g., as part of a fragment’s `partition_expression` or equivalent) so that PyArrow can use them for pruning without manual row-group scanning.

#### Scenario: Use stats to restrict fragments
- **WHEN** the catalog indicates that a file’s values for a column fall within a certain range
- **THEN** the fragment built for that file SHALL include an expression constraining that column’s range, of the form:
- `ds.field("<column>") >= <min_value>` AND `ds.field("<column>") <= <max_value>`
- **AND** PyArrow’s dataset engine SHALL be able to skip fragments that cannot satisfy the predicates.
