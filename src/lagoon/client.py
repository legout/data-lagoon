
from __future__ import annotations
from typing import Any, Optional

try:
    from unitycatalog import UnityCatalogClient  # type: ignore
except Exception:
    UnityCatalogClient = None  # type: ignore

class UCClient:
    def __init__(self, host: str, token: Optional[str] = None) -> None:
        self._host = host
        self._token = token
        self.client = UnityCatalogClient(host=host, token=token) if UnityCatalogClient else None

    def get_table(self, full_name: str) -> dict[str, Any]:
        if self.client:
            obj = self.client.tables.get(full_name)
            return obj if isinstance(obj, dict) else obj.__dict__
        return {"full_name": full_name, "data_source_format": "PARQUET", "storage_location": "", "schema": None}

    def list_tables(self, catalog: str, schema: str) -> list[dict[str, Any]]:
        if self.client:
            lst = self.client.tables.list(catalog, schema)
            if isinstance(lst, list):
                return [x if isinstance(x, dict) else x.__dict__ for x in lst]
        return []

    def create_table(self, **kwargs: Any) -> dict[str, Any]:
        if self.client:
            obj = self.client.tables.create(**kwargs)
            return obj if isinstance(obj, dict) else obj.__dict__
        return kwargs

    def drop_table(self, full_name: str) -> None:
        if self.client:
            self.client.tables.delete(full_name)
