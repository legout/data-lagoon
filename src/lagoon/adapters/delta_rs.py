
from __future__ import annotations
from typing import Any, Optional
from ..s3_config import S3Config

class DeltaAdapter:
    format = "DELTA"
    def __init__(self, *, storage_location: str, s3: S3Config, uc: Any) -> None:
        self.storage_location = storage_location
        self._s3 = s3
        self._uc = uc
    def to_arrow(self) -> Any: raise NotImplementedError
    def to_polars(self) -> Any: raise NotImplementedError
    def write(self, df: Any, mode: str = "append") -> None: raise NotImplementedError
    def delete(self, where: Optional[str] = None) -> None: raise NotImplementedError
