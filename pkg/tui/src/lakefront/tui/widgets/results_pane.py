from __future__ import annotations

from lakefront.core import ProjectContext
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import DataTable, Static


class ResultsPane(Widget):
    """Middle-bottom pane: query results as a scrollable DataTable."""

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    BINDINGS = [
        Binding("ctrl+e", "export", "Export CSV", show=True),
    ]

    DEFAULT_CSS = """
    ResultsPane {
        background: $surface;
    }

    ResultsPane > .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }

    ResultsPane > .meta-bar {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        height: 1;
    }

    ResultsPane DataTable {
        height: 1fr;
        border: none;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("RESULTS", classes="pane-title")
        yield Static(
            "no results yet — run a query with Ctrl+R",
            classes="meta-bar",
            id="meta-bar",
        )
        yield DataTable(id="results-table", zebra_stripes=True)

    def on_mount(self) -> None:
        table = self.query_one("#results-table", DataTable)
        table.cursor_type = "row"

    def load_dataframe(self, df) -> None:
        """Populate the DataTable from a pandas DataFrame."""
        table = self.query_one("#results-table", DataTable)
        table.clear(columns=True)
        for col in df.columns:
            table.add_column(f"{col} [{df[col].dtype}]", key=col)
        for row in df.itertuples(index=False):
            table.add_row(*[str(v) for v in row])
        meta = self.query_one("#meta-bar", Static)
        meta.update(f"✓ {len(df):,} rows · {len(df.columns)} cols")

    def action_export(self) -> None:
        self.notify("export CSV: not yet implemented")
