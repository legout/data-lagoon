from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import fsspec


@dataclass(frozen=True)
class FileSystemHandle:
    filesystem: fsspec.AbstractFileSystem
    root_path: str  # normalized path (no scheme)
    protocol: str


def resolve_filesystem(
    uri: str,
    *,
    storage_options: Optional[Dict[str, object]] = None,
) -> FileSystemHandle:
    fs, path = fsspec.url_to_fs(uri, **(storage_options or {}))
    protocol = _protocol_from_fs(fs)
    normalized_path = path or ""
    return FileSystemHandle(fs, normalized_path, protocol)


def _protocol_from_fs(fs: fsspec.AbstractFileSystem) -> str:
    protocol = getattr(fs, "protocol", "file")
    if isinstance(protocol, (list, tuple)):
        return protocol[0]
    return protocol
