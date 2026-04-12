from __future__ import annotations

from lakefront.core import ProjectContext
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import DataTable, Static


class ResultsPane(Widget):
    """Middle-bottom pane: query results as a scrollable DataTable."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.table = DataTable(id="results-table", zebra_stripes=True)

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
        yield self.table

    # def on_mount(self) -> None:
    #     table = self.query_one("#results-table", DataTable)
    #     table.cursor_type = "row"

    def action_export(self) -> None:
        self.notify("export CSV: not yet implemented")

    def run_query(self, sql: str) -> None:
        """Execute the query and display results."""
        try:
            df = self.ctx.query(sql).df()  # or however you run queries

            # Clear previous results
            self.table.clear()
            self.query_one("#meta-bar", Static).update(
                f"Executed: {sql[:50]}..." if len(sql) > 50 else f"Executed: {sql}"
            )

            # Add columns
            if not df.empty:
                self.table.columns.clear()
                self.table.add_columns(*df.columns)
                self.table.add_rows(df.itertuples(index=False, name=None))
                self.notify(f"Query returned {len(df)} rows", severity="information")
            else:
                self.notify("Query returned no rows", severity="information")

        except Exception as e:
            self.table.clear()
            self.notify(f"Error executing query:\n{str(e)}", severity="error")
