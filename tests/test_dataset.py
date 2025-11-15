from __future__ import annotations

import os
import pathlib
import sys
import tempfile
import unittest

import fsspec
import pyarrow as pa
import pyarrow.dataset as ds

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from data_lagoon import DatasetRef  # noqa: E402
from data_lagoon.dataset import DatasetError, read_dataset, write_dataset  # noqa: E402


class DatasetReadWriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_uri = os.path.join(self.temp_dir.name, "dataset")
        self.catalog_path = os.path.join(self.temp_dir.name, "catalog.db")
        self.catalog_uri = f"sqlite:///{self.catalog_path}"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_write_and_read_round_trip(self) -> None:
        table = pa.table({"value": [1, 2, 3]})
        result = write_dataset(
            "example",
            table,
            catalog_uri=self.catalog_uri,
            base_uri=self.base_uri,
        )
        self.assertEqual(len(result.files), 1)
        self.assertTrue(
            all(self._uri_exists(path) for path in result.files)
        )
        read_back = read_dataset(
            DatasetRef(name="example", base_uri=self.base_uri),
            catalog_uri=self.catalog_uri,
        )
        self.assertEqual(read_back.to_pydict(), {"value": [1, 2, 3]})
        self.assertEqual(result.version, 1)

    def test_write_requires_supported_type(self) -> None:
        with self.assertRaises(DatasetError):
            write_dataset(
                "example",
                data=object(),
                catalog_uri=self.catalog_uri,
                base_uri=self.base_uri,
            )

    def test_read_specific_version(self) -> None:
        table1 = pa.table({"value": [1, 2]})
        table2 = pa.table({"value": [3, 4]})
        write_dataset("example", table1, catalog_uri=self.catalog_uri, base_uri=self.base_uri)
        write_dataset("example", table2, catalog_uri=self.catalog_uri)

        latest = read_dataset("example", catalog_uri=self.catalog_uri)
        self.assertEqual(latest.to_pydict(), {"value": [3, 4]})

        previous = read_dataset("example", catalog_uri=self.catalog_uri, version=1)
        self.assertEqual(previous.to_pydict(), {"value": [1, 2]})

    def test_read_as_dataset(self) -> None:
        table = pa.table({"value": [1]})
        write_dataset("example", table, catalog_uri=self.catalog_uri, base_uri=self.base_uri)
        dataset_obj = read_dataset("example", catalog_uri=self.catalog_uri, as_dataset=True)
        self.assertIsInstance(dataset_obj, ds.Dataset)

    def _uri_exists(self, uri: str) -> bool:
        fs, path = fsspec.url_to_fs(uri)
        return fs.exists(path)


if __name__ == "__main__":
    unittest.main()
