from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.fs as pa_fs
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

        ds.write_dataset(
            data=table,
            base_dir=base_dir,
            format="parquet",
            basename_template=filename_template,
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


def read_dataset(
    ref_or_name: DatasetRef | str,
    *,
    catalog_uri: str = "sqlite:///:memory:",
    version: Optional[int] = None,
    as_dataset: bool = False,
) -> pa.Table | ds.Dataset:
    catalog = connect_catalog(catalog_uri)
    try:
        dataset = catalog.resolve_dataset(ref_or_name)
        effective_version = version or dataset.current_version
        if effective_version <= 0:
            raise DatasetError("Dataset has no committed versions to read")
        file_paths = catalog.list_files_for_version(dataset.id, effective_version)
    finally:
        catalog.close()

    if not file_paths:
        raise DatasetError(f"No files found for dataset version {effective_version}")

    first_handle = resolve_filesystem(file_paths[0])
    arrow_fs = _to_arrow_fs(first_handle)
    paths = [first_handle.root_path]
    for uri in file_paths[1:]:
        handle = resolve_filesystem(uri)
        if handle.protocol != first_handle.protocol:
            raise DatasetError("Mixed storage backends within a single version are not supported yet")
        paths.append(handle.root_path)

    dataset_obj = ds.dataset(paths, format="parquet", filesystem=arrow_fs)
    if as_dataset:
        return dataset_obj
    return dataset_obj.to_table()
