
from __future__ import annotations
from typing import Any
from .core import BaseTable, TableMetadata
from .adapters import delta_rs, pyiceberg_, pyarrow_
from .s3_config import S3Config

def build_table(meta: TableMetadata, *, s3: S3Config, uc: Any) -> BaseTable:
    fmt = meta.data_source_format.upper()
    if fmt == "DELTA":
        adapter = delta_rs.DeltaAdapter(storage_location=meta.storage_location, s3=s3, uc=uc)
    elif fmt == "ICEBERG":
        adapter = pyiceberg_.IcebergAdapter(full_name=meta.full_name, s3=s3, uc=uc)
    elif fmt == "PARQUET":
        adapter = pyarrow_.ParquetAdapter(storage_location=meta.storage_location, s3=s3, uc=uc)
    else:
        raise ValueError(f"Unsupported format: {fmt}")
    return BaseTable(meta, adapter)
