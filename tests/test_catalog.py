from __future__ import annotations

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from data_lagoon import (  # noqa: E402
    CatalogError,
    DatasetConflictError,
    DatasetIdentity,
    DatasetNotFoundError,
    DatasetRef,
    SqlCatalog,
    connect_catalog,
    looks_like_uri,
)


class CatalogCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = connect_catalog("sqlite:///:memory:")

    def tearDown(self) -> None:
        self.catalog.close()

    def test_register_dataset_is_idempotent(self) -> None:
        dataset_a = self.catalog.register_dataset("sales", "file:///tmp/sales")
        dataset_b = self.catalog.register_dataset("sales", "file:///tmp/sales")
        self.assertIsInstance(dataset_a, DatasetIdentity)
        self.assertEqual(dataset_a.id, dataset_b.id)
        self.assertEqual(dataset_a.base_uri, "file:///tmp/sales")

    def test_register_dataset_conflict_by_name(self) -> None:
        self.catalog.register_dataset("sales", "file:///tmp/sales")
        with self.assertRaises(DatasetConflictError):
            self.catalog.register_dataset("sales", "file:///tmp/other")

    def test_register_dataset_conflict_by_uri(self) -> None:
        self.catalog.register_dataset("sales", "file:///tmp/sales")
        with self.assertRaises(DatasetConflictError):
            self.catalog.register_dataset("marketing", "file:///tmp/sales")

    def test_resolve_dataset_by_name(self) -> None:
        created = self.catalog.register_dataset("sales", "file:///tmp/sales")
        resolved = self.catalog.resolve_dataset("sales")
        self.assertEqual(created, resolved)

    def test_resolve_dataset_by_uri(self) -> None:
        created = self.catalog.register_dataset("sales", "file:///tmp/sales")
        resolved = self.catalog.resolve_dataset("file:///tmp/sales")
        self.assertEqual(created, resolved)

    def test_resolve_missing_dataset_raises(self) -> None:
        with self.assertRaises(DatasetNotFoundError):
            self.catalog.resolve_dataset("nonexistent")

    def test_resolve_missing_dataset_by_uri_requires_name(self) -> None:
        with self.assertRaises(DatasetNotFoundError):
            self.catalog.resolve_dataset("file:///tmp/sales")
        with self.assertRaises(CatalogError):
            self.catalog.resolve_dataset(
                DatasetRef(base_uri="file:///tmp/sales"), create_if_missing=True
            )

        created = self.catalog.resolve_dataset(
            DatasetRef(base_uri="file:///tmp/sales"), create_if_missing=True, name="sales"
        )
        self.assertEqual(created.name, "sales")

    def test_resolve_missing_dataset_by_name_requires_base_uri(self) -> None:
        with self.assertRaises(CatalogError):
            self.catalog.resolve_dataset("sales", create_if_missing=True)
        created = self.catalog.resolve_dataset(
            "sales", create_if_missing=True, base_uri="file:///tmp/sales"
        )
        self.assertEqual(created.base_uri, "file:///tmp/sales")

    def test_list_datasets_returns_registered_entries(self) -> None:
        self.catalog.register_dataset("sales", "file:///tmp/sales")
        self.catalog.register_dataset("marketing", "file:///tmp/marketing")
        datasets = self.catalog.list_datasets()
        self.assertEqual([d.name for d in datasets], ["sales", "marketing"])


class HelperFunctionTests(unittest.TestCase):
    def test_looks_like_uri(self) -> None:
        self.assertTrue(looks_like_uri("s3://bucket/path"))
        self.assertTrue(looks_like_uri("/tmp/data"))
        self.assertFalse(looks_like_uri("dataset_name"))


class DatasetRefTests(unittest.TestCase):
    def test_from_legacy_parses_uri(self) -> None:
        ref = DatasetRef.from_legacy("s3://bucket/path")
        self.assertEqual(ref.base_uri, "s3://bucket/path")
        self.assertIsNone(ref.name)

    def test_from_legacy_parses_name(self) -> None:
        ref = DatasetRef.from_legacy("sales")
        self.assertEqual(ref.name, "sales")
        self.assertIsNone(ref.base_uri)

    def test_canonical_uri_with_dataset_id(self) -> None:
        ref = DatasetRef(catalog_uri="sqlite:///tmp/catalog.db", dataset_id=42)
        uri = ref.canonical_uri()
        self.assertTrue(uri.startswith("lagoon://"))
        self.assertIn("dataset_id=42", uri)

    def test_canonical_uri_with_name(self) -> None:
        ref = DatasetRef(catalog_uri="sqlite:///tmp/catalog.db", name="sales")
        uri = ref.canonical_uri()
        self.assertTrue(uri.endswith("/datasets/sales"))


if __name__ == "__main__":
    unittest.main()
