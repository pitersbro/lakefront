from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from .config import Settings, load_settings
from .models import DataSource, Project


@dataclass
class Source:
    ctx: ProjectContext
    source: DataSource
    path: Path = field(init=False)
    data: ds.Dataset = field(init=False)

    def __post_init__(self):
        self.path = Path(self.source.path)
        self.data = ds.dataset(self.path.as_posix(), format="parquet")

    def __str__(self):
        return f"{self.source.name} ({self.source.kind})"


@dataclass
class QueryResult:
    relation: duckdb.DuckDBPyRelation
    sql: str

    def df(self) -> pd.DataFrame:
        return self.relation.fetchdf()

    def arrow(self) -> pa.Table:
        return self.relation.arrow()

    def __getattr__(self, item):
        # Proxy any missing attributes to the underlying relation
        return getattr(self.relation, item)


class QueryEngineMixin:
    settings: Settings
    _con: duckdb.DuckDBPyConnection | None = None

    def get_connection(self):
        if hasattr(self, "_con") and self._con is not None:
            return self._con

        settings = self.settings

        conn = duckdb.connect(
            database=":memory:",
            read_only=False,
            config={
                "threads": settings.duckdb.threads,
                "memory_limit": settings.duckdb.memory_limit,
            },
        )
        self._con = conn
        return self._con

    def register_source(self, source: Source):
        conn = self.get_connection()
        conn.register(source.source.name, source.data)

    def query(self, sql: str) -> QueryResult:
        conn = self.get_connection()
        return QueryResult(relation=conn.sql(sql), sql=sql)


@dataclass
class ProjectContext(QueryEngineMixin):
    """In-memory representation of a project configuration,
    with additional methods for querying and profiling.


    Examples:
        ctx = ProjectContext.from_model(project_model)
        print(ctx.list_source_names())
        result = ctx.query("SELECT * FROM my_source LIMIT 10").fetchdf()
    """

    name: str
    profile: str
    _sources: list[DataSource]
    sources: list[Source] = field(init=False)

    settings: Settings = field(init=False)

    def __post_init__(self):
        self.settings = load_settings(profile=self.profile)
        self.sources = [Source(self, src) for src in self._sources]
        for source in self.sources:
            self.register_source(source)

    @classmethod
    def from_model(cls, project: Project) -> ProjectContext:
        return cls(
            name=project.name,
            profile=project.profile,
            _sources=project.sources,
        )

    def list_source_names(self) -> list[str]:
        return [src.source.name for src in self.sources]
