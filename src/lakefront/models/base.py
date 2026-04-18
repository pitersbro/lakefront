from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from lakefront import util

SourceKind = Literal["local", "s3"]


class DuckDBConfig(BaseModel):
    threads: int = 4
    memory_limit: str = "2GB"


class S3Config(BaseModel):
    endpoint: str = "http://localhost:9000"
    access_key: str = Field(default="root", json_schema_extra={"secret": True})
    secret_key: str = Field(default="password", json_schema_extra={"secret": True})
    region: str = "us-east-1"

    @property
    def endpoint_host(self):
        return self.endpoint.removeprefix("http://").removeprefix("https://")

    @property
    def endpoint_ssl(self):
        return self.endpoint.startswith("https://")

    @property
    def url_scheme(self):
        return "https" if self.endpoint_ssl else "http"


class DataSource(BaseModel):
    name: str
    path: str  # local path or s3://bucket/prefix
    description: str = ""


class Project(BaseModel):
    name: str
    description: str = ""
    profile: str = "default"
    sources: list[DataSource] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=util.utcnow)
    updated_at: datetime = Field(default_factory=util.utcnow)
