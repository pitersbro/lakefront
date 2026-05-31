from dataclasses import dataclass

import duckdb
import pandas as pd
import pyarrow as pa

from lakefront.log import logger

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


class QueryEngineMixin:
    settings: Settings
    _con: duckdb.DuckDBPyConnection | None = None

    def configure_s3(self):
        con = self.get_connection()
        logger.debug("Configuring S3 access for DuckDB...")
        try:
            con.execute("LOAD httpfs;")
        except duckdb.IOException:
            try:
                con.execute("INSTALL httpfs; LOAD httpfs;")
            except duckdb.IOException as e:
                raise RuntimeError(
                    "Failed to load httpfs extension. "
                    "Run `python -m lakefront install` to pre-install dependencies."
                ) from e

        ssl = "true" if self.settings.s3.endpoint_ssl else "false"

        con.execute(
            f"""
            SET s3_access_key_id='{self.settings.s3.access_key}';
            SET s3_secret_access_key='{self.settings.s3.secret_key}';
            SET s3_endpoint='{self.settings.s3.endpoint_host}';
            SET s3_region='{self.settings.s3.region}';
            SET s3_use_ssl           = {ssl};
            SET s3_url_style         = 'path';
            """
        )
        logger.debug("S3 configuration complete.")

    def get_connection(self):
        if self._con is not None:
            return self._con

        conn = duckdb.connect(
            database=":memory:",
            read_only=False,
            config={
                "threads": self.settings.duckdb.threads,
                "memory_limit": self.settings.duckdb.memory_limit,
            },
        )
        self._con = conn
        return self._con

    def query(self, sql: str) -> QueryResult:
        conn = self.get_connection()
        return QueryResult(relation=conn.sql(sql), sql=sql)
