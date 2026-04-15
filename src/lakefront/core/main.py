from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import duckdb
import pandas as pd
import pyarrow as pa

from .config import ProjectConfigurationService, Settings, load_settings
from .exceptions import SourceNotFoundError, SourceTypeInvalidError
from .log import logger
from .models import DataSource, Project

SourceType = Literal["parquet", "dataset", "csv"]


@dataclass
class Source:
    ctx: ProjectContext
    source: DataSource
    path: Path = field(init=False)
    type: SourceType = field(init=False)

    @property
    def name(self) -> str:
        return self.source.name

    def __post_init__(self):
        self.path = Path(self.source.path)
        self._resolve_type()

    def _resolve_type(self):
        if self.path.is_file() and self.path.suffix == ".parquet":
            self.type = "parquet"
            return
        elif self.path.is_dir() and any(
            p.suffix == ".parquet" for p in self.path.rglob("*.parquet")
        ):
            self.type = "dataset"
            return
        elif self.path.is_file() and self.path.suffix == ".csv":
            self.type = "csv"
            return
        raise SourceTypeInvalidError(f"Unsupported source type for path: {self.path}")

    def __str__(self):
        return f"{self.source.name} ({self.source.kind})"

    def __repr__(self):
        return f"Source(name={self.name}, type={self.type}, path='{self.path}')"


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
        name = source.source.name
        path = source.path.as_posix()
        reader = "read_parquet"
        if source.type == "csv":
            reader = "read_csv_auto"
        elif source.type == "dataset":
            path = f"{path}/**/*.parquet"
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
    with additional methods for querying and profiling.


    Examples:
        ctx = ProjectContext.from_model(project_model)
        print(ctx.list_source_names())
        result = ctx.query("SELECT * FROM my_source LIMIT 10").fetchdf()
        ctx.describe_source("my_source")
        ctx.group_sources_by_type()

    """

    name: str
    profile: str
    _sources: list[DataSource]
    sources: list[Source] = field(init=False)

    settings: Settings = field(init=False)

    def __post_init__(self):
        self.settings = load_settings(profile=self.profile)
        self.sources = []
        for src in self._sources:
            try:
                source = Source(self, src)
                if not source.path.exists():
                    raise SourceNotFoundError(
                        f"Source path does not exist: {source.path}"
                    )
                self.sources.append(source)
            except (SourceNotFoundError, SourceTypeInvalidError) as e:
                logger.error(f"Skipping source '{src.name}' due to error: {e}")

        for source in self.sources:
            self.register_source(source)

    @classmethod
    def from_model(cls, project: Project) -> ProjectContext:
        return cls(
            name=project.name,
            profile=project.profile,
            _sources=project.sources,
        )

    def sources_by_type(self) -> dict[str, list[str]]:
        groups: dict[SourceType, list[str]] = {}
        for src in self.sources:
            groups.setdefault(src.type, []).append(src.name)
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

        new_source = DataSource(name=name, kind=kind, path=path)
        ProjectConfigurationService.add_source(self.name, new_source)
        return self.reinitialize()

    def source_detach(self, name: str) -> ProjectContext:
        """Detach a source from the project and reinitialize the context."""
        if not any(s.name == name for s in self.sources):
            raise SourceNotFoundError(f'Source with name "{name}" not found.')

        ProjectConfigurationService.remove_source(self.name, name)
        self.deregister_source(name)
        return self.reinitialize()
