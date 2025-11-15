"""
Public package interface for data_lagoon.
"""

from .catalog import (
    CatalogError,
    DatasetConflictError,
    DatasetIdentity,
    DatasetNotFoundError,
    DatasetRef,
    SqlCatalog,
    connect_catalog,
    looks_like_uri,
)
from .dataset import DatasetError, WriteResult, read_dataset, write_dataset

__all__ = [
    "CatalogError",
    "DatasetConflictError",
    "DatasetIdentity",
    "DatasetNotFoundError",
    "DatasetRef",
    "SqlCatalog",
    "connect_catalog",
    "looks_like_uri",
    "DatasetError",
    "WriteResult",
    "write_dataset",
    "read_dataset",
]


def hello() -> str:
    return "Hello from data-lagoon!"
