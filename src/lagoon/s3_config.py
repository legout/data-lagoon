
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class S3Config:
    endpoint: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    path_style: bool = True

    def storage_options(self) -> Dict[str, Any]:
        opts: Dict[str, Any] = {}
        if self.endpoint:
            opts["AWS_ENDPOINT_URL"] = self.endpoint
        if self.region:
            opts["AWS_REGION"] = self.region
        if self.access_key:
            opts["AWS_ACCESS_KEY_ID"] = self.access_key
        if self.secret_key:
            opts["AWS_SECRET_ACCESS_KEY"] = self.secret_key
        return opts

    def arrow_filesystem_kwargs(self) -> Dict[str, Any]:
        return {
            "endpoint_override": self.endpoint,
            "region": self.region or "us-east-1",
            "access_key": self.access_key,
            "secret_key": self.secret_key,
        }
