from __future__ import annotations

from dataclasses import dataclass, field

import duckdb
import pandas as pd
import pyarrow as pa

from lakefront import models, util

from .config import ProjectConfigurationService, Settings, load_settings
from .exceptions import SourceNotFoundError


@dataclass
class Source:
    ctx: ProjectContext
    source: models.DataSource
    info: util.PathInfo = field(init=False)

    def __post_init__(self):
        self.info = util.PathInfo(self.source.path, self.ctx.profile)

    @property
    def name(self) -> str:
        return self.source.name


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

    _CREATE_VIEW_TAMPLATE = """
        CREATE VIEW IF NOT EXISTS {name} 
        AS SELECT * FROM {reader}('{path}')
        """
    _DROP_VIEW_TEMPLATE = "DROP VIEW IF EXISTS {name}"

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
        name = source.name
        reader = "read_parquet"
        path = source.info.path
        if source.info.is_csv():
            reader = "read_csv_auto"
        elif source.info.is_dataset():
            path = f"{source.info.path}/**/*.parquet"
        if source.info.is_s3():
            path = f"s3://{path}"
        sql = self._CREATE_VIEW_TAMPLATE.format(
            name=name, reader=reader, path=path
        ).strip()
        conn.execute(sql)

    def deregister_source(self, name: str):
        conn = self.get_connection()
        sql = self._DROP_VIEW_TEMPLATE.format(name=name).strip()
        conn.execute(sql)

    def query(self, sql: str) -> QueryResult:
        conn = self.get_connection()
        return QueryResult(relation=conn.sql(sql), sql=sql)


@dataclass
class ProjectContext(QueryEngineMixin):
    """In-memory representation of a project configuration,
    with additional methods for querying and profiling."""

    name: str
    profile: str
    _sources: list[models.DataSource]
    sources: list[Source] = field(init=False)

    settings: Settings = field(init=False)

    def __post_init__(self):
        self.settings = load_settings(profile=self.profile)
        self.sources = []
        for src in self._sources:
            source = Source(self, src)
            if source.info.exists():
                self.sources.append(source)

        for source in self.sources:
            self.register_source(source)

    @classmethod
    def from_model(cls, project: models.Project) -> ProjectContext:
        return cls(
            name=project.name,
            profile=project.profile,
            _sources=project.sources,
        )

    def sources_by_type(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for src in self.sources:
            groups.setdefault(src.info.get_type().value, []).append(src.name)
        sorted_groups = {
            k: sorted(v) for k, v in sorted(groups.items(), key=lambda x: x[0])
        }
        return sorted_groups

    def source_names(self) -> list[str]:
        return [src.source.name for src in self.sources]

    def source_get(self, name: str) -> Source:
        source = next((s for s in self.sources if s.name == name), None)
        if not source:
            raise SourceNotFoundError(
                f'Source with name "{name}" not found in project.'
            )
        return source

    def source_describe(self, name: str) -> QueryResult:
        src = self.source_get(name)
        return self.query(f"DESCRIBE {src.name}")

    def reinitialize(self) -> ProjectContext:
        """Reinitialize the project context, reloading all sources and settings."""
        project = ProjectConfigurationService.get(self.name)
        obj = ProjectContext.from_model(project)
        self.__dict__.update(obj.__dict__)
        return self

    def source_attach(self, name: str, path: str, kind: str) -> ProjectContext:
        """Attach a new source to the project and reinitialize the context."""
        if any(s.name == name for s in self.sources):
            raise ValueError(f'Source with name "{name}" already exists.')

        new_source = models.DataSource(name=name, path=path)
        ProjectConfigurationService.add_source(self.name, new_source)
        return self.reinitialize()

    def source_detach(self, name: str) -> ProjectContext:
        """Detach a source from the project and reinitialize the context."""
        if not any(s.name == name for s in self.sources):
            raise SourceNotFoundError(f'Source with name "{name}" not found.')

        ProjectConfigurationService.remove_source(self.name, name)
        self.deregister_source(name)
        return self.reinitialize()
