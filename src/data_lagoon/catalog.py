from __future__ import annotations

import contextlib
from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from typing import Any, Dict, Optional, Sequence, Tuple
from urllib.parse import ParseResult, urlparse, urlunparse

try:  # DuckDB is optional; import lazily so it is not a hard dependency.
    import duckdb  # type: ignore
except Exception:  # pragma: no cover - duckdb is optional at runtime.
    duckdb = None  # type: ignore


__all__ = [
    "CatalogError",
    "DatasetConflictError",
    "DatasetNotFoundError",
    "DatasetIdentity",
    "DatasetRef",
    "SqlCatalog",
    "connect_catalog",
    "looks_like_uri",
]


class CatalogError(RuntimeError):
    """Base class for catalog-related failures."""


class DatasetNotFoundError(CatalogError):
    """Raised when a dataset reference cannot be resolved."""


class DatasetConflictError(CatalogError):
    """Raised when attempting to create a dataset that conflicts with existing metadata."""


@dataclass(frozen=True)
class DatasetIdentity:
    """Represents a dataset registered in the catalog."""

    id: int
    name: str
    base_uri: str
    current_version: int
    created_at: datetime


@dataclass(frozen=True)
class DatasetRef:
    """
    Structured dataset reference used by public APIs.

    The reference may include:
    - ``catalog_uri``: location of the catalog service (e.g., ``sqlite:///...`` or ``postgresql://...``).
    - ``dataset_id``: numeric identifier assigned by the catalog.
    - ``name``: human-readable dataset name.
    - ``base_uri``: storage location for the dataset.
    - ``version``: optional version number (used by read APIs).
    - ``metadata``: optional free-form dictionary (e.g., tags, owner).
    """

    catalog_uri: Optional[str] = None
    dataset_id: Optional[int] = None
    name: Optional[str] = None
    base_uri: Optional[str] = None
    version: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    def with_updates(self, **updates: Any) -> "DatasetRef":
        data = {
            "catalog_uri": self.catalog_uri,
            "dataset_id": self.dataset_id,
            "name": self.name,
            "base_uri": self.base_uri,
            "version": self.version,
            "metadata": self.metadata,
        }
        data.update(updates)
        return DatasetRef(**data)

    def canonical_uri(self) -> str:
        """
        Produce a canonical dataset URI if possible.

        Examples:
        - ``lagoon://catalog-uri?dataset_id=123`` when ``dataset_id`` is known.
        - ``lagoon://catalog-uri/datasets/<name>`` when only name is known.
        - ``dataset:<id>`` as a fallback when only the identifier is available.
        """

        if self.catalog_uri and self.dataset_id is not None:
            parsed = urlparse(self.catalog_uri)
            query = f"dataset_id={self.dataset_id}"
            canonical = ParseResult(
                scheme="lagoon",
                netloc=parsed.netloc or parsed.path,
                path="/",
                params="",
                query=query,
                fragment="",
            )
            return urlunparse(canonical)

        if self.catalog_uri and self.name:
            parsed = urlparse(self.catalog_uri)
            path = f"/datasets/{self.name}"
            canonical = ParseResult(
                scheme="lagoon",
                netloc=parsed.netloc or parsed.path,
                path=path,
                params="",
                query="",
                fragment="",
            )
            return urlunparse(canonical)

        if self.dataset_id is not None:
            return f"dataset:{self.dataset_id}"

        raise CatalogError("Cannot generate canonical URI without catalog information")

    @classmethod
    def from_legacy(cls, value: str | "DatasetRef") -> "DatasetRef":
        if isinstance(value, DatasetRef):
            return value
        if looks_like_uri(value):
            return cls(base_uri=value)
        return cls(name=value)


_SCHEMA_STATEMENTS: Tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        base_uri TEXT NOT NULL UNIQUE,
        current_version INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS schema_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL REFERENCES datasets(id),
        version INTEGER NOT NULL,
        arrow_schema BLOB NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(dataset_id, version)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL REFERENCES datasets(id),
        version INTEGER NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        operation TEXT NOT NULL,
        metadata_json TEXT,
        UNIQUE(dataset_id, version)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dataset_id INTEGER NOT NULL REFERENCES datasets(id),
        version INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        file_size_bytes INTEGER,
        row_count INTEGER,
        schema_version_id INTEGER REFERENCES schema_versions(id),
        metadata_json TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        is_tombstoned INTEGER NOT NULL DEFAULT 0,
        UNIQUE(dataset_id, file_path, version)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS row_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL REFERENCES files(id),
        row_group_index INTEGER NOT NULL,
        stats_min_json TEXT,
        stats_max_json TEXT,
        null_counts_json TEXT,
        row_count INTEGER,
        UNIQUE(file_id, row_group_index)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS partitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id INTEGER NOT NULL REFERENCES files(id),
        key TEXT NOT NULL,
        value TEXT NOT NULL
    );
    """,
)


def looks_like_uri(value: str) -> bool:
    """
    Heuristically determine whether the given string looks like a URI/base path.

    A string containing a scheme (e.g. ``s3://``) or an absolute path is treated
    as a URI; other strings are assumed to be dataset names.
    """

    parsed = urlparse(value)
    if parsed.scheme:
        return True
    return value.startswith("/") or value.startswith(".")


class SqlCatalog:
    """
    Lightweight relational catalog for datasets.

    The catalog expects a DB-API compliant connection whose placeholder format
    matches SQLite/DuckDB (``?``). DuckDB support is optional at runtime; other
    engines (e.g. PostgreSQL) can be integrated by providing a compatible
    connection object.
    """

    def __init__(self, connection: Any, backend: str = "sqlite") -> None:
        self._connection = connection
        self._backend = backend
        self._configure_connection()
        self.ensure_schema()

    @property
    def backend(self) -> str:
        return self._backend

    def _configure_connection(self) -> None:
        if isinstance(self._connection, sqlite3.Connection):
            self._connection.row_factory = sqlite3.Row

    # ------------------------------------------------------------------ schema
    def ensure_schema(self) -> None:
        """Create catalog tables if they do not already exist."""

        for statement in _SCHEMA_STATEMENTS:
            self._connection.execute(statement)
        self._ensure_files_table_columns()
        self._connection.commit()

    def _ensure_files_table_columns(self) -> None:
        cursor = self._connection.execute("PRAGMA table_info(files)")
        columns = {row[1] for row in cursor.fetchall()}
        if "schema_version_id" not in columns:
            self._connection.execute(
                "ALTER TABLE files ADD COLUMN schema_version_id INTEGER REFERENCES schema_versions(id)"
            )
        if "metadata_json" not in columns:
            self._connection.execute(
                "ALTER TABLE files ADD COLUMN metadata_json TEXT"
            )

    # ------------------------------------------------------------ dataset ops
    def register_dataset(self, name: str, base_uri: str) -> DatasetIdentity:
        """
        Insert a dataset into the catalog if it does not exist, otherwise return
        the existing dataset. Raises DatasetConflictError if the name exists with
        a different base URI.
        """

        existing = self.get_dataset_by_name(name)
        if existing:
            if existing.base_uri != base_uri:
                raise DatasetConflictError(
                    f"Dataset '{name}' already exists with base URI '{existing.base_uri}'"
                )
            return existing

        existing_by_uri = self.get_dataset_by_uri(base_uri)
        if existing_by_uri:
            if existing_by_uri.name != name:
                raise DatasetConflictError(
                    f"Base URI '{base_uri}' already belongs to dataset '{existing_by_uri.name}'"
                )
            return existing_by_uri

        cursor = self._connection.execute(
            "INSERT INTO datasets (name, base_uri) VALUES (?, ?)", (name, base_uri)
        )
        dataset_id = cursor.lastrowid
        self._connection.commit()
        return self.get_dataset_by_id(dataset_id)

    def get_dataset_by_name(self, name: str) -> Optional[DatasetIdentity]:
        cursor = self._connection.execute(
            "SELECT id, name, base_uri, current_version, created_at FROM datasets WHERE name = ?",
            (name,),
        )
        row = cursor.fetchone()
        return self._row_to_dataset(cursor, row)

    def get_dataset_by_uri(self, base_uri: str) -> Optional[DatasetIdentity]:
        cursor = self._connection.execute(
            "SELECT id, name, base_uri, current_version, created_at FROM datasets WHERE base_uri = ?",
            (base_uri,),
        )
        row = cursor.fetchone()
        return self._row_to_dataset(cursor, row)

    def get_dataset_by_id(self, dataset_id: int) -> DatasetIdentity:
        cursor = self._connection.execute(
            "SELECT id, name, base_uri, current_version, created_at FROM datasets WHERE id = ?",
            (dataset_id,),
        )
        row = cursor.fetchone()
        dataset = self._row_to_dataset(cursor, row)
        if not dataset:
            raise DatasetNotFoundError(f"Dataset id {dataset_id} not found")
        return dataset

    def resolve_dataset(
        self,
        reference: DatasetIdentity | DatasetRef | str,
        *,
        create_if_missing: bool = False,
        base_uri: Optional[str] = None,
        name: Optional[str] = None,
    ) -> DatasetIdentity:
        """
        Resolve a dataset identity by name or URI. When ``create_if_missing`` is
        True, missing datasets may be created if the complementary information
        is provided.
        """

        if isinstance(reference, DatasetIdentity):
            return reference

        ref = DatasetRef.from_legacy(reference)
        ref_name = ref.name or name
        ref_base_uri = ref.base_uri or base_uri

        if ref.dataset_id is not None:
            return self.get_dataset_by_id(ref.dataset_id)

        if ref.base_uri:
            dataset = self.get_dataset_by_uri(ref.base_uri)
            if dataset:
                return dataset
            if create_if_missing:
                if not ref_name:
                    raise CatalogError(
                        "name is required to create a dataset when resolving by URI"
                    )
                return self.register_dataset(name=ref_name, base_uri=ref.base_uri)
            raise DatasetNotFoundError(
                f"No dataset registered for URI '{ref.base_uri}'"
            )

        if ref_name:
            dataset = self.get_dataset_by_name(ref_name)
            if dataset:
                return dataset
            if create_if_missing:
                if not ref_base_uri:
                    raise CatalogError(
                        "base_uri is required to create a dataset when resolving by name"
                    )
                return self.register_dataset(name=ref_name, base_uri=ref_base_uri)

        raise DatasetNotFoundError(
            f"Dataset reference could not be resolved: {reference!r}"
        )

    # -------------------------------------------------------------- utilities
    def list_datasets(self) -> Sequence[DatasetIdentity]:
        cursor = self._connection.execute(
            "SELECT id, name, base_uri, current_version, created_at FROM datasets ORDER BY id"
        )
        rows = cursor.fetchall()
        return [
            dataset
            for row in rows
            if (dataset := self._row_to_dataset(cursor, row)) is not None
        ]

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self._connection.close()

    # ---------------------------------------------------------- write helpers
    def record_write_with_metadata(
        self,
        dataset: DatasetIdentity,
        *,
        version: int,
        files: Sequence[dict[str, Any]],
    ) -> DatasetIdentity:
        if version <= dataset.current_version:
            raise CatalogError(
                f"Version {version} must be greater than current {dataset.current_version}"
            )

        if not files:
            raise CatalogError("At least one file record is required for a write")

        with self._connection:  # begins transaction
            self._connection.execute(
                "INSERT INTO transactions (dataset_id, version, operation) VALUES (?, ?, ?)",
                (dataset.id, version, "append"),
            )

            for entry in files:
                schema_bytes = entry.get("schema_bytes")
                schema_version_id = (
                    self._get_or_create_schema_version(dataset.id, schema_bytes)
                    if schema_bytes is not None
                    else None
                )

                cursor = self._connection.execute(
                    """
                    INSERT INTO files (
                        dataset_id,
                        version,
                        file_path,
                        file_size_bytes,
                        row_count,
                        schema_version_id,
                        metadata_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        dataset.id,
                        version,
                        entry["file_path"],
                        entry.get("file_size_bytes"),
                        entry.get("row_count"),
                        schema_version_id,
                        json.dumps(entry.get("metadata_dict")) if entry.get("metadata_dict") else None,
                    ),
                )
                file_id = cursor.lastrowid
                self._persist_row_groups(file_id, entry.get("row_groups") or [])
                self._persist_partitions(file_id, entry.get("partitions") or {})

            self._connection.execute(
                "UPDATE datasets SET current_version = ? WHERE id = ?",
                (version, dataset.id),
            )

        return self.get_dataset_by_id(dataset.id)

    def _get_or_create_schema_version(
        self, dataset_id: int, schema_bytes: Optional[bytes]
    ) -> Optional[int]:
        if schema_bytes is None:
            return None
        cursor = self._connection.execute(
            "SELECT id FROM schema_versions WHERE dataset_id = ? AND arrow_schema = ?",
            (dataset_id, schema_bytes),
        )
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor = self._connection.execute(
            "SELECT COALESCE(MAX(version), -1) FROM schema_versions WHERE dataset_id = ?",
            (dataset_id,),
        )
        next_version = (cursor.fetchone()[0] or -1) + 1
        cursor = self._connection.execute(
            """
            INSERT INTO schema_versions (dataset_id, version, arrow_schema)
            VALUES (?, ?, ?)
            """,
            (dataset_id, next_version, schema_bytes),
        )
        return cursor.lastrowid

    def _persist_row_groups(
        self, file_id: int, row_groups: Sequence[dict[str, Any]]
    ) -> None:
        for rg in row_groups:
            self._connection.execute(
                """
                INSERT INTO row_groups (
                    file_id,
                    row_group_index,
                    row_count,
                    stats_min_json,
                    stats_max_json,
                    null_counts_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    file_id,
                    rg.get("row_group_index"),
                    rg.get("row_count"),
                    json.dumps(rg.get("stats_min")),
                    json.dumps(rg.get("stats_max")),
                    json.dumps(rg.get("null_counts")),
                ),
            )

    def _persist_partitions(
        self, file_id: int, partitions: Dict[str, str]
    ) -> None:
        for key, value in partitions.items():
            self._connection.execute(
                "INSERT INTO partitions (file_id, key, value) VALUES (?, ?, ?)",
                (file_id, key, value),
            )

    def list_files_for_version(
        self, dataset_id: int, version: int
    ) -> Sequence[str]:
        cursor = self._connection.execute(
            """
            SELECT file_path FROM files
            WHERE dataset_id = ? AND version = ?
            ORDER BY id
            """,
            (dataset_id, version),
        )
        rows = cursor.fetchall()
        return [row[0] if not hasattr(row, "keys") else row["file_path"] for row in rows]

    # ------------------------------------------------------------ row helpers
    def _row_to_dataset(self, cursor: Any, row: Any) -> Optional[DatasetIdentity]:
        if row is None:
            return None

        mapping: dict[str, Any]
        if hasattr(row, "keys"):
            mapping = {key: row[key] for key in row.keys()}
        else:
            description = getattr(cursor, "description", None)
            if not description:
                raise CatalogError("Cannot determine column names for dataset row")
            mapping = {description[i][0]: value for i, value in enumerate(row)}

        created_at_value = mapping.get("created_at")
        if isinstance(created_at_value, datetime):
            created_at = created_at_value
        else:
            created_at = datetime.fromisoformat(str(created_at_value))

        return DatasetIdentity(
            id=int(mapping["id"]),
            name=str(mapping["name"]),
            base_uri=str(mapping["base_uri"]),
            current_version=int(mapping["current_version"]),
            created_at=created_at,
        )


def connect_catalog(uri: str) -> SqlCatalog:
    """
    Create a catalog for the given connection URI.

    Supported URI schemes:
    - ``sqlite:///<path>`` or ``sqlite:///:memory:`` (default)
    - ``duckdb:///<path>`` (requires the optional ``duckdb`` package)
    """

    parsed = urlparse(uri)
    scheme = parsed.scheme or "sqlite"

    if scheme == "sqlite":
        path = parsed.path or ":memory:"
        if path in ("", "/", "/:memory:", ":memory:"):
            db_path = ":memory:"
        elif path.startswith("/"):
            # sqlite:///tmp/db.db -> path "/tmp/db.db"
            db_path = path
        else:
            db_path = path
        connection = sqlite3.connect(db_path)
        return SqlCatalog(connection, backend="sqlite")

    if scheme == "duckdb":
        if duckdb is None:  # pragma: no cover - optional dependency
            raise CatalogError(
                "duckdb:// URI requires the 'duckdb' package to be installed"
            )
        path = parsed.path or ":memory:"
        connection = duckdb.connect(database=path or ":memory:")
        return SqlCatalog(connection, backend="duckdb")

    raise CatalogError(f"Unsupported catalog scheme '{scheme}'")
