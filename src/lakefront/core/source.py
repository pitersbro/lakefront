from __future__ import annotations

from dataclasses import dataclass

import duckdb

from lakefront import models

from . import exceptions, fs
from .context import Context, get_context

CREATE_VIEW_TAMPLATE = """
CREATE VIEW IF NOT EXISTS {name} 
AS SELECT * FROM {reader}('{path}')
"""
DROP_VIEW_TEMPLATE = "DROP VIEW IF EXISTS {name}"

# TODO: Promote PathType to SourceType
SourceType = fs.PathType | str


@dataclass
class Source:
    uri: str
    name: str

    def reachable(self) -> bool: ...

    @property
    def ctx(self) -> Context:
        return get_context()

    def get_type(self) -> str: ...

    def register(self, con: duckdb.DuckDBPyConnection): ...


@dataclass
class LocalFile(Source):
    def __post_init__(self):
        self._info = fs.PathInfo(self.uri, profile=self.ctx.profile)

    def reachable(self) -> bool:
        return self._info.exists()

    def get_type(self):
        return self._info.get_type().value

    def register(self, con: duckdb.DuckDBPyConnection):
        name = self.name
        reader = "read_parquet"
        path = self._info.path
        if self._info.is_csv():
            reader = "read_csv_auto"
        elif self._info.is_dataset():
            path = f"{self._info.path}/**/*.parquet"
        sql = CREATE_VIEW_TAMPLATE.format(name=name, reader=reader, path=path).strip()
        con.execute(sql)

    def deregister(self, con: duckdb.DuckDBPyConnection):
        name = self.name
        sql = DROP_VIEW_TEMPLATE.format(name=name).strip()
        con.execute(sql)


S3File = LocalFile


def resolve(model: models.DataSource) -> Source:
    scheme = model.get_scheme()
    match scheme:
        case "file" | None | "":
            return LocalFile(uri=model.uri, name=model.name)
        case "s3":
            return S3File(uri=model.uri, name=model.name)
        case _:
            raise exceptions.SourceTypeInnvalidError(
                f"Unsupported URI scheme: {scheme}"
            )
