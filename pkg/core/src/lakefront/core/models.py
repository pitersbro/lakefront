from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

SourceKind = Literal["local", "s3"]


def utcnow():
    return datetime.now(tz=timezone.utc)


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
