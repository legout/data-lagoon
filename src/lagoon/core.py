from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class TableMetadata:
    full_name: str
    data_source_format: str
    storage_location: str
    schema_json: dict | None = None

class BaseTable:
    def __init__(self, meta: TableMetadata, adapter: Any):
        self.meta = meta
        self._adapter = adapter

    def to_arrow(self) -> Any:
        return self._adapter.to_arrow()

    def to_polars(self) -> Any:
        return self._adapter.to_polars()

    def write(self, df: Any, mode: str = "append") -> None:
        self._adapter.write(df, mode)

    def delete(self, where: str | None = None) -> None:
        self._adapter.delete(where)
