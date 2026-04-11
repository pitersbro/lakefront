from __future__ import annotations

from lakefront.core import ProjectContext
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static


class ProfilerPane(Widget):
    """Right pane: summary statistics for the active source or result."""

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    DEFAULT_CSS = """
    ProfilerPane {
        background: $surface;
        padding: 0;
    }

    ProfilerPane > .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }

    ProfilerPane .stat-label {
        color: $text-disabled;
        padding: 0 1;
        height: 1;
    }

    ProfilerPane .stat-value {
        color: $text;
        padding: 0 2;
        height: 1;
        text-style: bold;
    }

    ProfilerPane .stat-sub {
        color: $text-muted;
        padding: 0 2;
        height: 1;
    }

    ProfilerPane .divider {
        color: $panel;
        height: 1;
        padding: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("PROFILER", classes="pane-title")
        yield Static("─" * 26, classes="divider")
        yield Static("rows (total)", classes="stat-label")
        yield Static("—", classes="stat-value", id="stat-rows")
        yield Static("─" * 26, classes="divider")
        yield Static("null rates", classes="stat-label")
        yield Static("—", classes="stat-value", id="stat-nulls")
        yield Static("─" * 26, classes="divider")
        yield Static("columns", classes="stat-label")
        yield Static("—", classes="stat-value", id="stat-cols")
        yield Static("─" * 26, classes="divider")
        yield Static("select a source", classes="stat-sub", id="stat-hint")

    def update_stats(self, df) -> None:
        """Update profiler stats from a pandas DataFrame."""
        rows = f"{len(df):,}"
        cols = str(len(df.columns))
        null_pct = df.isnull().mean().mul(100).round(1)
        top_null = null_pct[null_pct > 0].sort_values(ascending=False)

        self.query_one("#stat-rows", Static).update(rows)
        self.query_one("#stat-cols", Static).update(cols)

        if top_null.empty:
            self.query_one("#stat-nulls", Static).update("none")
        else:
            summary = "  ".join(f"{c}: {v}%" for c, v in top_null.head(3).items())
            self.query_one("#stat-nulls", Static).update(summary)

        self.query_one("#stat-hint", Static).update("")
