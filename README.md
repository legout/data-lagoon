# data-lagoon

Pythonic Parquet lakehouse utilities.

## Installing data-lagoon

```bash
pip install data-lagoon
```

### Remote filesystems

`data-lagoon` relies on [fsspec](https://filesystem-spec.readthedocs.io/) to talk to object stores. Install the extras for the backends you need:

- `pip install "data-lagoon[s3]"` for Amazon S3 (`s3://` URIs; requires `s3fs`)
- `pip install "data-lagoon[gcs]"` for Google Cloud Storage (`gs://`; requires `gcsfs`)
- `pip install "data-lagoon[azure]"` for Azure Data Lake/Blob (`abfs://` / `abfss://`; requires `adlfs`)

Credentials/configuration are handled by each fsspec backend (environment variables, config files, IAM roles, etc.).
