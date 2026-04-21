import pandas as pd

from .base import ContextBase


class Analyzer:
    def __init__(self, ctx: ContextBase):
        self.ctx = ctx
        # TODO: Make it confiurable via project.toml core section
        self._limit = 50000

    def analyze_sql(self, sql: str) -> dict:
        """Run a SQL query and profile the resulting DataFrame."""
        result = self.ctx.query(sql)
        df = result.df()
        return self.analyze_pandas(df, name="query_result")

    def analyze_source(self, source_name: str) -> dict:
        """Profile an entire source by sampling it with a SQL query."""
        sql = f'SELECT * FROM "{source_name}" LIMIT 50000'
        result = self.ctx.query(sql)
        df = result.df()
        return self.analyze_pandas(df, name=source_name)

    @classmethod
    def analyze_pandas(cls, df: pd.DataFrame, name: str) -> dict:
        """Compute a compact statistical profile of a DataFrame."""
        profile: dict = {
            "source": name,
            "rows": len(df),
            "columns": len(df.columns),
            "schema": {},
            "stats": {},
            "sample": df.head(5).to_dict(orient="records"),
        }

        for col in df.columns:
            dtype = str(df[col].dtype)
            null_pct = round(df[col].isnull().mean() * 100, 1)
            profile["schema"][col] = {"type": dtype, "null_pct": null_pct}

            if pd.api.types.is_numeric_dtype(df[col]):
                s = df[col].dropna()
                profile["stats"][col] = {
                    "min": float(s.min()) if len(s) else None,
                    "max": float(s.max()) if len(s) else None,
                    "mean": round(float(s.mean()), 4) if len(s) else None,
                    "median": round(float(s.median()), 4) if len(s) else None,
                    "std": round(float(s.std()), 4) if len(s) else None,
                    "p25": round(float(s.quantile(0.25)), 4) if len(s) else None,
                    "p75": round(float(s.quantile(0.75)), 4) if len(s) else None,
                }
            elif pd.api.types.is_object_dtype(df[col]) or isinstance(
                df[col].dtype, pd.CategoricalDtype
            ):
                vc = df[col].value_counts().head(5).to_dict()
                profile["stats"][col] = {
                    "unique": int(df[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in vc.items()},
                }

        return profile
