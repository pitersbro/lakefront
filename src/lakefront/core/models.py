from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

SourceKind = Literal["local", "s3"]


def utcnow():
    return datetime.now(tz=timezone.utc)


class DuckDBConfig(BaseModel):
    threads: int = 4
    memory_limit: str = "2GB"


class S3Config(BaseModel):
    endpoint: str = "http://localhost:9000"
    access_key: str = Field(default="root", json_schema_extra={"secret": True})
    secret_key: str = Field(default="password", json_schema_extra={"secret": True})


class DataSource(BaseModel):
    name: str
    kind: SourceKind
    path: str  # local path or s3://bucket/prefix
    description: str = ""


class Project(BaseModel):
    name: str
    description: str = ""
    profile: str = "default"
    sources: list[DataSource] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
