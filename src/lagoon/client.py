from __future__ import annotations
import httpx
from typing import Any

class UCClient:
    """Minimal Unity Catalog REST client (stub for Phase 1)."""
    def __init__(self, base_url: str):
        self._base = base_url.rstrip('/')
        self._http = httpx.Client(timeout=30.0)

    def get_table(self, full_name: str) -> dict[str, Any]:
        r = self._http.get(f"{self._base}/api/2.1/unity-catalog/tables/{full_name}")
        r.raise_for_status()
        return r.json()

    def list_tables(self, catalog: str, schema: str) -> list[dict[str, Any]]:
        r = self._http.get(f"{self._base}/api/2.1/unity-catalog/tables", params={"catalog_name": catalog, "schema_name": schema})
        r.raise_for_status()
        return r.json().get("tables", [])

    def drop_table(self, full_name: str) -> None:
        r = self._http.delete(f"{self._base}/api/2.1/unity-catalog/tables/{full_name}")
        r.raise_for_status()
