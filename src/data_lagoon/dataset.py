from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.fs as pa_fs
import pyarrow.parquet as pq
from pyarrow.dataset import WrittenFile

from .catalog import DatasetRef, connect_catalog
from .storage import FileSystemHandle, resolve_filesystem


def _to_arrow_fs(fs_handle: FileSystemHandle) -> pa_fs.FileSystem:
    return pa_fs.PyFileSystem(pa_fs.FSSpecHandler(fs_handle.filesystem))


class DatasetError(RuntimeError):
    """Raised when read/write operations fail."""


@dataclass
class WriteResult:
    dataset_ref: DatasetRef
    row_count: int
    files: Sequence[str]
    version: int
    file_metadata: Sequence[dict[str, Any]] = ()


PredicateInput = Tuple[str, str, Any]


@dataclass(frozen=True)
class Predicate:
    column: str
    op: str
    value: Any


try:  # optional dependency
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - pandas optional
    pd = None  # type: ignore

try:  # optional dependency
    import polars as pl  # type: ignore
except Exception:  # pragma: no cover - polars optional
    pl = None  # type: ignore


def _normalize_to_table(data: Any) -> pa.Table:
    if isinstance(data, pa.Table):
        return data
    if isinstance(data, pa.RecordBatch):
        return pa.Table.from_batches([data])
    if isinstance(data, pa.RecordBatchReader):
        return pa.Table.from_batches(list(data))
    if pd is not None and isinstance(data, pd.DataFrame):  # type: ignore[arg-type]
        return pa.Table.from_pandas(data)
    if pl is not None and isinstance(data, pl.DataFrame):  # type: ignore[attr-defined]
        return data.to_arrow()
    raise DatasetError(f"Unsupported data type for write_dataset: {type(data)!r}")


def _prepare_write_destination(fs_handle: FileSystemHandle, version: int) -> Tuple[str, str]:
    sep = getattr(fs_handle.filesystem, "sep", "/")
    base_root = fs_handle.root_path.rstrip(sep)
    version_dir = f"{base_root}{sep}v{version}" if base_root else f"v{version}"
    fs_handle.filesystem.makedirs(version_dir, exist_ok=True)
    basename_template = f"part-v{version}-{{i}}.parquet"
    return version_dir, basename_template


def _extract_partitions(relative_path: str, sep: str) -> Dict[str, str]:
    segments = [segment for segment in relative_path.split(sep) if segment]
    partitions: Dict[str, str] = {}
    for segment in segments:
        if "=" in segment:
            key, value = segment.split("=", 1)
            partitions[key] = value
    return partitions


def _extract_row_groups(metadata: Optional[pa.parquet.FileMetaData]) -> List[dict[str, Any]]:
    if metadata is None:
        return []
    meta_dict = metadata.to_dict()
    row_groups: List[dict[str, Any]] = []
    for idx, rg in enumerate(meta_dict.get("row_groups", [])):
        stats_min: Dict[str, Any] = {}
        stats_max: Dict[str, Any] = {}
        null_counts: Dict[str, Any] = {}
        for column in rg.get("columns", []):
            stats = column.get("statistics") or {}
            name = column.get("path_in_schema") or column.get("name")
            if name is None:
                continue
            if "min" in stats:
                stats_min[name] = stats["min"]
            if "max" in stats:
                stats_max[name] = stats["max"]
            if "null_count" in stats:
                null_counts[name] = stats["null_count"]
        row_groups.append(
            {
                "row_group_index": idx,
                "row_count": rg.get("num_rows"),
                "stats_min": stats_min,
                "stats_max": stats_max,
                "null_counts": null_counts,
            }
        )
    return row_groups


def write_dataset(
    ref_or_name: DatasetRef | str,
    data: Any,
    *,
    catalog_uri: str = "sqlite:///:memory:",
    base_uri: Optional[str] = None,
    partition_by: Optional[Sequence[str]] = None,
) -> WriteResult:
    catalog = connect_catalog(catalog_uri)
    try:
        dataset = catalog.resolve_dataset(
            ref_or_name, create_if_missing=True, base_uri=base_uri
        )

        if not dataset.base_uri:
            raise DatasetError("Dataset has no base_uri configured")

        table = _normalize_to_table(data)
        schema_bytes = table.schema.serialize().to_pybytes()
        version = dataset.current_version + 1
        fs_handle = resolve_filesystem(dataset.base_uri)
        base_dir, filename_template = _prepare_write_destination(fs_handle, version)

        written_files: List[Dict[str, Any]] = []

        sep = getattr(fs_handle.filesystem, "sep", "/")

        root_marker = getattr(fs_handle.filesystem, "root_marker", "")

        def _visitor(written: WrittenFile) -> None:
            if root_marker and written.path.startswith(root_marker):
                relative_path = written.path
            else:
                relative_path = f"{base_dir}{sep}{written.path}".replace(f"{sep}{sep}", sep)
            absolute_path = fs_handle.filesystem.unstrip_protocol(relative_path)
            row_count = written.metadata.num_rows if written.metadata else None
            try:
                size = fs_handle.filesystem.size(relative_path)
            except Exception:
                size = None
            partitions = _extract_partitions(relative_path, sep)
            written_files.append(
                {
                    "file_path": absolute_path,
                    "row_count": row_count,
                    "file_size_bytes": size,
                    "partitions": partitions,
                    "row_groups": _extract_row_groups(written.metadata),
                    "schema_bytes": schema_bytes,
                    "metadata_dict": written.metadata.to_dict() if written.metadata else None,
                }
            )

        arrow_fs = _to_arrow_fs(fs_handle)

        partitioning = (
            ds.partitioning(pa.schema([(name, table.schema.field(name).type) for name in partition_by]), flavor="hive")
            if partition_by
            else None
        )

        ds.write_dataset(
            data=table,
            base_dir=base_dir,
            format="parquet",
            basename_template=filename_template,
            partitioning=partitioning,
            existing_data_behavior="overwrite_or_ignore",
            file_visitor=_visitor,
            filesystem=arrow_fs,
        )

        if not written_files:
            raise DatasetError("write_dataset produced no output files")

        updated_dataset = catalog.record_write_with_metadata(
            dataset,
            version=version,
            files=written_files,
        )
    finally:
        catalog.close()

    total_rows = sum(entry.get("row_count") or 0 for entry in written_files)

    return WriteResult(
        dataset_ref=DatasetRef(
            name=updated_dataset.name,
            base_uri=updated_dataset.base_uri,
            dataset_id=updated_dataset.id,
            catalog_uri=catalog_uri,
        ),
        row_count=total_rows,
        files=[entry["file_path"] for entry in written_files],
        version=version,
        file_metadata=[entry.get("metadata_dict") or {} for entry in written_files],
    )


def parse_predicates(predicates: Optional[Sequence[PredicateInput]]) -> List[Predicate]:
    result: List[Predicate] = []
    if not predicates:
        return result
    for column, op, value in predicates:
        normalized_op = op.strip().lower()
        if normalized_op not in {"=", "==", "<", "<=", ">", ">="}:
            raise DatasetError(f"Unsupported predicate operator '{op}'")
        if normalized_op == "=":
            normalized_op = "=="
        result.append(Predicate(column=column, op=normalized_op, value=value))
    return result


def read_dataset(
    ref_or_name: DatasetRef | str,
    *,
    catalog_uri: str = "sqlite:///:memory:",
    version: Optional[int] = None,
    as_dataset: bool = False,
    predicates: Optional[Sequence[PredicateInput]] = None,
) -> pa.Table | ds.Dataset:
    catalog = connect_catalog(catalog_uri)
    try:
        dataset = catalog.resolve_dataset(ref_or_name)
        effective_version = version or dataset.current_version
        if effective_version <= 0:
            raise DatasetError("Dataset has no committed versions to read")
        file_records = catalog.list_file_records_for_version(dataset.id, effective_version)
    finally:
        catalog.close()

    if not file_records:
        raise DatasetError(f"No files found for dataset version {effective_version}")

    parsed_predicates = parse_predicates(predicates)
    pruned_files = _prune_files_and_row_groups(
        catalog_uri=catalog_uri,
        dataset_id=dataset.id,
        version=effective_version,
        file_records=file_records,
        predicates=parsed_predicates,
    )

    if not pruned_files:
        raise DatasetError("No data matches the provided predicates")

    any_path = pruned_files[0]["file_path"]
    first_handle = resolve_filesystem(any_path)
    arrow_fs = _to_arrow_fs(first_handle)

    paths: List[str] = []
    row_group_map: Dict[str, Dict[str, Any]] = {}
    for record in pruned_files:
        uri = record["file_path"]
        handle = resolve_filesystem(uri)
        if handle.protocol != first_handle.protocol:
            raise DatasetError("Mixed storage backends within a single version are not supported yet")
        paths.append(handle.root_path)
        row_group_map[handle.root_path] = {
            "row_groups": record.get("row_groups"),
            "partitions": record.get("partitions") or {},
        }

    dataset_obj = ds.dataset(paths, format="parquet", filesystem=arrow_fs)
    if as_dataset:
        return dataset_obj
    return _materialize_table_with_row_groups(dataset_obj, arrow_fs, row_group_map)


def _prune_files_and_row_groups(
    *,
    catalog_uri: str,
    dataset_id: int,
    version: int,
    file_records: Sequence[dict[str, Any]],
    predicates: Sequence[Predicate],
) -> List[dict[str, Any]]:
    if not predicates:
        return [
            {"file_path": record["file_path"], "row_groups": None} for record in file_records
        ]

    catalog = connect_catalog(catalog_uri)
    try:
        file_ids = [record["id"] for record in file_records]
        partition_map = catalog.fetch_partitions_for_files(file_ids)
        row_group_map = catalog.fetch_row_groups_for_files(file_ids)
    finally:
        catalog.close()

    eq_partition_filters = {
        pred.column: pred.value for pred in predicates if pred.op == "=="
    }

    result: List[dict[str, Any]] = []
    for record in file_records:
        file_id = record["id"]
        file_path = record["file_path"]
        partitions = partition_map.get(file_id, {})

        if not _partitions_match(partition_map.get(file_id, {}), eq_partition_filters):
            continue

        selected_row_groups = _filter_row_groups(
            row_group_map.get(file_id, []), predicates
        )
        if selected_row_groups is not None and not selected_row_groups:
            continue

        result.append(
            {
                "file_path": file_path,
                "row_groups": selected_row_groups,
                "partitions": partitions,
            }
        )

    if not result:
        # Fall back to scanning all files if pruning removed everything
        return [
            {
                "file_path": record["file_path"],
                "row_groups": None,
                "partitions": partition_map.get(record["id"], {}),
            }
            for record in file_records
        ]
    return result


def _partitions_match(
    file_partitions: Dict[str, str],
    equality_filters: Dict[str, Any],
) -> bool:
    for key, expected in equality_filters.items():
        actual = file_partitions.get(key)
        if actual is None:
            continue
        if str(actual) != str(expected):
            return False
    return True


def _filter_row_groups(
    row_group_records: Sequence[dict[str, Any]],
    predicates: Sequence[Predicate],
) -> Optional[List[int]]:
    if not predicates or not row_group_records:
        return None

    selected: List[int] = []
    for record in row_group_records:
        stats_min = (
            json.loads(record["stats_min_json"]) if record.get("stats_min_json") else {}
        )
        stats_max = (
            json.loads(record["stats_max_json"]) if record.get("stats_max_json") else {}
        )

        matches_all = True
        for predicate in predicates:
            if not _row_group_matches(stats_min, stats_max, predicate):
                matches_all = False
                break
        if matches_all:
            selected.append(record.get("row_group_index", 0))

    return selected if selected else None


def _row_group_matches(
    stats_min: Dict[str, Any],
    stats_max: Dict[str, Any],
    predicate: Predicate,
) -> bool:
    min_val = stats_min.get(predicate.column)
    max_val = stats_max.get(predicate.column)
    if min_val is None or max_val is None:
        return True

    value = predicate.value
    if predicate.op == "==":
        return min_val <= value <= max_val
    if predicate.op == ">":
        return max_val > value
    if predicate.op == ">=":
        return max_val >= value
    if predicate.op == "<":
        return min_val < value
    if predicate.op == "<=":
        return min_val <= value
    return True


def _materialize_table_with_row_groups(
    dataset_obj: ds.Dataset,
    filesystem: pa_fs.FileSystem,
    row_group_map: Dict[str, Dict[str, Any]],
) -> pa.Table:
    if not any(entry.get("row_groups") for entry in row_group_map.values()):
        return dataset_obj.to_table()

    tables: List[pa.Table] = []
    for path, entry in row_group_map.items():
        row_groups = entry.get("row_groups")
        partitions = entry.get("partitions") or {}
        if row_groups:
            with filesystem.open_input_file(path) as handle:
                parquet_file = pq.ParquetFile(handle)
                table = parquet_file.read_row_groups(row_groups)
        else:
            subset = ds.dataset([path], format="parquet", filesystem=filesystem)
            table = subset.to_table()

        if partitions:
            table = _append_partition_columns(table, partitions)
        tables.append(table)

    if not tables:
        return dataset_obj.to_table()
    return pa.concat_tables(tables) if len(tables) > 1 else tables[0]


def _append_partition_columns(table: pa.Table, partitions: Dict[str, str]) -> pa.Table:
    result = table
    for key, value in partitions.items():
        array = pa.array([value] * result.num_rows)
        result = result.append_column(key, array)
    return result
