import pandas as pd

from .base import ContextBase
from .exceptions import LlmError

SYSTEM_PROMPT = """\
You are a senior data analyst. You receive a statistical profile of a dataset
and the user's question. Provide clear, concise, actionable insights.
Use markdown with headers and bullet points. Be specific — reference actual
column names, values and numbers from the profile.
"""


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
        rows, cols = df.shape
        profile: dict = {
            "source": name,
            "rows": rows,
            "columns": cols,
            "schema": {},
            "stats": {},
            "sample": df.head(5).to_dict(orient="records"),
        }

        for col in df.columns:
            dtype = str(df[col].dtype)
            null_pct = round(df[col].isnull().mean() * 100, 1)
            profile["schema"][col] = {"type": dtype, "null_pct": null_pct}
            if pd.api.types.is_bool_dtype(df[col]):
                vc = df[col].value_counts(dropna=False).to_dict()
                profile["stats"][col] = {
                    "unique": int(df[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in vc.items()},
                }

            elif pd.api.types.is_numeric_dtype(df[col]):
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
            elif (
                pd.api.types.is_object_dtype(df[col])
                or isinstance(df[col].dtype, pd.CategoricalDtype)
                or isinstance(df[col].dtype, pd.StringDtype)
            ):
                vc = df[col].value_counts().head(100).to_dict()
                profile["stats"][col] = {
                    "unique": int(df[col].nunique()),
                    "top_values": {str(k): int(v) for k, v in vc.items()},
                }

        return profile

    @classmethod
    def render_profile(cls, profile: dict) -> str:
        lines: list[str] = [
            f"[bold]Rows:[/bold]    {profile['rows']:,}",
            f"[bold]Columns:[/bold] {profile['columns']}",
            "─" * 36,
        ]
        for col, meta in profile["schema"].items():
            lines.append(f"[bold]{col}[/bold]")
            lines.append(f"  type:  {meta['type']}")
            lines.append(f"  nulls: {meta['null_pct']}%")
            stats = profile["stats"].get(col, {})
            if "mean" in stats:
                lines.append(f"  min/max: {stats['min']} / {stats['max']}")
                lines.append(f"  mean: {stats['mean']}  median: {stats['median']}")
            elif "unique" in stats:
                lines.append(f"  unique: {stats['unique']}")
                top = ", ".join(
                    f"{k}({v})" for k, v in list(stats["top_values"].items())[:3]
                )
                lines.append(f"  top: {top}")
            lines.append("─" * 36)

        return "\n".join(lines)

    def llm_enabled(self) -> bool:
        return (
            self.ctx.settings.anthropic.enabled is True
            and self.ctx.settings.anthropic.api_key != ""
            and self.ctx.settings.anthropic.url != ""
        )

    def ask_llm(self, question: str, profile: dict) -> str:
        if not self.llm_enabled():
            raise LlmError("LLM is disabled. Please check your settings.")

        url = self.ctx.settings.anthropic.url
        api_key = self.ctx.settings.anthropic.api_key
        import json

        import httpx

        profile_json = json.dumps(profile, indent=2, default=str)
        user_msg = (
            f"Dataset profile:\n```json\n{profile_json}\n```\n\nQuestion: {question}"
        )
        try:
            response = httpx.post(
                url + "/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_msg}],
                },
                timeout=60,
            )
            data = response.json()
            if response.status_code != 200:
                raise LlmError(
                    f"LLM API error: {response.status_code} {response.reason_phrase}\n{str(data)}"
                )
            md = data["content"][0]["text"].strip()
        except Exception as e:
            md = f"**Error:** {e}"
        return md
