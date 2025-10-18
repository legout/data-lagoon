from __future__ import annotations
from .core import BaseTable, TableMetadata
from .adapters import delta_rs, pyiceberg_, pyarrow_

def build_table(meta: TableMetadata) -> BaseTable:
    fmt = meta.data_source_format.upper()
    if fmt == "DELTA":
        adapter = delta_rs.DeltaAdapter(meta.storage_location)
    elif fmt == "ICEBERG":
        adapter = pyiceberg_.IcebergAdapter(meta.full_name)
    elif fmt == "PARQUET":
        adapter = pyarrow_.ParquetAdapter(meta.storage_location)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    return BaseTable(meta, adapter)
