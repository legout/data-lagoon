from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import pyarrow as pa
import pyarrow.ipc as ipc


class SchemaMismatchError(ValueError):
    """Raised when dataset schema evolution cannot be performed."""


@dataclass
class MergeResult:
    schema: pa.Schema
    casts: Dict[str, pa.DataType]
    schema_changed: bool


def serialize_schema(schema: pa.Schema) -> bytes:
    return schema.serialize().to_pybytes()


def deserialize_schema(data: bytes) -> pa.Schema:
    reader = ipc.open_stream(pa.BufferReader(data))
    return reader.schema


_PROMOTION_MAP = {
    pa.int32(): pa.int64(),
    pa.int64(): pa.float64(),
    pa.float32(): pa.float64(),
}


def merge_schemas(
    current: Optional[pa.Schema],
    incoming: pa.Schema,
    *,
    schema_merge: bool,
    promote_to_string: bool,
) -> MergeResult:
    if current is None:
        return MergeResult(schema=incoming, casts={}, schema_changed=True)

    incoming_fields = {field.name: field for field in incoming}
    new_fields = []
    casts: Dict[str, pa.DataType] = {}
    schema_changed = False

    for field in current:
        incoming_field = incoming_fields.pop(field.name, None)
        if incoming_field is None:
            raise SchemaMismatchError(
                f"Incoming data is missing required column '{field.name}'"
            )
        merged_field, cast_type, changed = _merge_field(
            field,
            incoming_field,
            schema_merge=schema_merge,
            promote_to_string=promote_to_string,
        )
        new_fields.append(merged_field)
        if cast_type is not None:
            casts[field.name] = cast_type
        schema_changed = schema_changed or changed

    if incoming_fields and not schema_merge:
        raise SchemaMismatchError("New columns are not allowed when schema_merge is False")

    # Remaining incoming fields are new columns
    for name, incoming_field in incoming_fields.items():
        schema_changed = True
        new_fields.append(incoming_field.with_nullable(True))

    return MergeResult(schema=pa.schema(new_fields), casts=casts, schema_changed=schema_changed)


def _merge_field(
    current_field: pa.Field,
    incoming_field: pa.Field,
    *,
    schema_merge: bool,
    promote_to_string: bool,
) -> tuple[pa.Field, Optional[pa.DataType], bool]:
    current_type = current_field.type
    incoming_type = incoming_field.type

    if incoming_type.equals(current_type):
        nullable = current_field.nullable or incoming_field.nullable
        return current_field.with_nullable(nullable), None, False

    if not schema_merge:
        raise SchemaMismatchError(
            f"Column '{current_field.name}' has incompatible type and schema merging is disabled"
        )

    target_type = _resolve_type(current_type, incoming_type, promote_to_string)
    nullable = current_field.nullable or incoming_field.nullable
    field_changed = not target_type.equals(current_type)
    return (
        pa.field(current_field.name, target_type, nullable=nullable),
        target_type,
        field_changed,
    )


def _resolve_type(
    current_type: pa.DataType,
    incoming_type: pa.DataType,
    promote_to_string: bool,
) -> pa.DataType:
    if promote_to_string:
        return pa.string()

    for source, target in _PROMOTION_MAP.items():
        if current_type.equals(source) and incoming_type.equals(target):
            return target

    if incoming_type.equals(current_type):
        return current_type

    raise SchemaMismatchError(
        f"Cannot merge column types '{current_type}' and '{incoming_type}'"
    )


def align_table_to_schema(table: pa.Table, result: MergeResult) -> pa.Table:
    columns = []
    for field in result.schema:
        column = table.column(field.name)
        cast_type = result.casts.get(field.name)
        if cast_type is not None:
            column = column.cast(cast_type)
        columns.append(column)
    return pa.table(columns, schema=result.schema)
