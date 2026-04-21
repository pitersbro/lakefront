from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import duckdb
import pandas as pd
import pyarrow as pa

from lakefront import models, util

from .config import Settings


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


@dataclass
class Source:
    ctx: ContextBase
    source: models.DataSource
    info: util.PathInfo = field(init=False)

    def __post_init__(self):
        self.info = util.PathInfo(self.source.path, self.ctx.profile)

    @property
    def name(self) -> str:
        return self.source.name


@dataclass
class ContextBase:
    """In-memory representation of a project configuration,
    with additional methods for querying and profiling."""

    name: str
    profile: str
    _sources: list[models.DataSource]
    sources: list[Source] = field(init=False)

    settings: Settings = field(init=False)
    log_file: Path = field(init=False)

    def query(self, sql: str) -> QueryResult:
        raise NotImplementedError("Subclasses must implement query method.")
