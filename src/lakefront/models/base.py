from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator

from lakefront import util


class AppConfig(BaseModel):
    theme: str = Field(
        default="tokyo-night",
        description="The theme to use for the TUI. This can be overridden by project settings.",
    )


class CoreConfig(BaseModel):
    theme: str = Field(
        default="tokyo-night",
        description="The default theme for a project. Overrides the app theme if app is run in a project context.",
    )
    analyzer_row_limit: int = 0


class DuckDBConfig(BaseModel):
    threads: int = 4
    memory_limit: str = "2GB"


class AnthropicConfig(BaseModel):
    url: str = "https://api.anthropic.com/v1"
    api_key: str = Field(default="", json_schema_extra={"secret": True})
    model: str = Field(
        default="claude-sonnet-4-6",
        description="Anthropic model id used for dataset insights.",
    )
    enabled: bool = Field(default=False, description="Whether to enable LLM features")


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


_PASSTHROUGH_SCHEMES = {
    "http",
    "https",
    "ftp",
    "s3",
    "postgresql",
    "postgres",
    "sqlite",
    "sqlite3",
    "resource",
    "pkg",
}


class DataSource(BaseModel):
    name: str
    uri: str  # local path or s3://bucket/prefix
    description: str = ""

    @model_validator(mode="before")
    @classmethod
    def _accept_path(cls, data: dict) -> dict:
        if "path" in data and "uri" not in data:
            data["uri"] = data.pop("path")
        return data

    @field_validator("uri", mode="before")
    @classmethod
    def normalise_uri(cls, v: object) -> str:
        if not isinstance(v, str):
            raise ValueError(f"uri must be a string, got {type(v).__name__}")

        v = v.strip()
        scheme = urlparse(v).scheme

        if scheme == "file":
            # normalise file:// → expand ~ just in case
            path = Path(v[7:]).expanduser().resolve()
            return path.as_uri()  # file:///abs/path

        if scheme in _PASSTHROUGH_SCHEMES:
            return v  # pass through known schemes

        # bare local path (old TOML): ~/foo, /abs/foo, relative/foo
        # single-char scheme = Windows drive letter e.g. C:/foo
        if not scheme or len(scheme) == 1:
            return Path(v).expanduser().resolve().as_uri()  # → file:///abs/path

        return v  # unknown scheme, pass through

    def get_scheme(self) -> str:
        return urlparse(self.uri).scheme or "file"


class Project(BaseModel):
    name: str
    description: str = ""
    profile: str = "default"
    sources: list[DataSource] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=util.utcnow)
    updated_at: datetime = Field(default_factory=util.utcnow)
