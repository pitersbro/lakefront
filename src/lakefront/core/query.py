import duckdb

from lakefront.log import logger

from .base import QueryResult, Source
from .config import Settings


class QueryEngineMixin:
    settings: Settings
    _con: duckdb.DuckDBPyConnection | None = None

    _CREATE_VIEW_TAMPLATE = """
        CREATE VIEW IF NOT EXISTS {name} 
        AS SELECT * FROM {reader}('{path}')
        """
    _DROP_VIEW_TEMPLATE = "DROP VIEW IF EXISTS {name}"

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

    def register_source(self, source: Source):
        conn = self.get_connection()
        logger.debug(
            f'Registering source "{source.name}" with path: {source.info.path}'
        )
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
