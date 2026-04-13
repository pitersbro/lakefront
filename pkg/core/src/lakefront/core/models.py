from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from .exceptions import SourceNotFoundError

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

    @model_validator(mode="after")
    def source_path(self):
        if self.kind == "local":
            path = Path(self.path)
            if not path.exists():
                raise SourceNotFoundError(f"Source path does not exist: {self.path}")
        return self


class Project(BaseModel):
    name: str
    description: str = ""
    profile: str = "default"
    sources: list[DataSource] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
