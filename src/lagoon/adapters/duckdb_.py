
from __future__ import annotations
from typing import Any
from ..s3_config import S3Config

class DuckDBQueryEngine:
    def __init__(self, uc: Any, s3: S3Config) -> None:
        self._uc = uc
        self._s3 = s3
    def sql(self, sql_text: str) -> Any:
        raise NotImplementedError
