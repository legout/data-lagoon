from __future__ import annotations
from typing import Any, Optional
from .client import UCClient
from .dispatch import build_table
from .core import BaseTable, TableMetadata
from .s3_config import S3Config


class Lagoon:
    def __init__(
        self,
        uc_url: str,
        token: Optional[str] = None,
        *,
        s3_endpoint: Optional[str] = None,
        s3_region: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        path_style: bool = True,
    ) -> None:
        self.uc = UCClient(host=uc_url, token=token)
        self.s3 = S3Config(
            endpoint=s3_endpoint,
            region=s3_region,
            access_key=access_key,
            secret_key=secret_key,
            path_style=path_style,
        )

    def get_table(self, full_name: str) -> BaseTable:
        meta_dict = self.uc.get_table(full_name)
        meta = TableMetadata(
            full_name=meta_dict["full_name"],
            data_source_format=meta_dict.get("data_source_format", "PARQUET"),
            storage_location=meta_dict.get("storage_location", ""),
            schema_json=meta_dict.get("schema"),
        )
        return build_table(meta, s3=self.s3, uc=self.uc)

    def read(self, full_name: str) -> BaseTable:
        return self.get_table(full_name)

    def write(
        self, df: Any, full_name: str, *, format: str, mode: str = "append", **options: Any
    ) -> None:
        table = self.get_table(full_name)
        table.write(df, mode=mode)

    def sql(self, sql_text: str, *, backend: str = "duckdb") -> Any:
        if backend == "duckdb":
            from .adapters.duckdb_ import DuckDBQueryEngine

            engine = DuckDBQueryEngine(self.uc, self.s3)
        elif backend == "datafusion":
            from .adapters.datafusion_ import DataFusionQueryEngine

            engine = DataFusionQueryEngine(self.uc, self.s3)
        else:
            raise ValueError(f"Unknown backend: {backend}")
        return engine.sql(sql_text)

    def describe(self, full_name: str) -> dict:
        return self.uc.get_table(full_name)

    def list_tables(
        self, qualified: str | None = None, *, catalog: str | None = None, schema: str | None = None
    ) -> list[dict]:
        if qualified:
            c, s = qualified.split(".", 1)
            return self.uc.list_tables(c, s)
        if catalog and schema:
            return self.uc.list_tables(catalog, schema)
        raise ValueError("Provide either qualified='catalog.schema' or catalog= and schema=")

    def drop_table(self, full_name: str) -> None:
        self.uc.drop_table(full_name)

    def register(
        self, path: str, as_table: str, *, format: str, columns: list[dict] | None = None
    ) -> dict:
        return self.uc.create_table(
            full_name=as_table,
            data_source_format=format.upper(),
            storage_location=path,
            columns=columns or [],
            table_type="EXTERNAL",
        )

    def refresh(self, full_name: str) -> None:
        _ = self.get_table(full_name)
