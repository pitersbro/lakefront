from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import DataTable, Static

from lakefront.core import ProjectContext
from lakefront.tui.screens.explore import ExploreScreen


class ResultsPane(Widget):
    """Middle-bottom pane: query results as a scrollable DataTable."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.table = DataTable(id="results-table", zebra_stripes=True)
        self.table.cursor_type = "row"
        self._sql = None
        self.border_title = "Results"

    BINDINGS = [
        Binding("x", "export", "Export to file", show=True),
        Binding("e", "explore", "Explore", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            "no results yet — run a query with Ctrl+R",
            classes="meta-bar",
            id="meta-bar",
        )
        yield self.table

    def action_export(self) -> None:
        self.notify("export not yet implemented")

    def _update_table(self, sql: str, df) -> None:
        """Helper to update the DataTable with new results."""
        if not df.empty:
            self.table.add_columns(*df.columns)
            self.table.add_rows(df.itertuples(index=False, name=None))
            self.query_one("#meta-bar", Static).update(
                f"Executed: {sql[:50]}..." if len(sql) > 50 else f"Executed: {sql}"
            )
            self.notify(f"Query returned {len(df)} rows", severity="information")
        else:
            self.query_one("#meta-bar", Static).update(
                f"Executed: {sql[:50]}..." if len(sql) > 50 else f"Executed: {sql}"
            )
            self.notify("Query returned no rows", severity="information")

    def action_explore(self) -> None:
        if self._sql is None:
            self.notify("No data to explore", severity="warning")
            return

        self.app.push_screen(ExploreScreen(self.ctx, "query", self._sql))

    @work(thread=True)
    def run_query(self, sql: str) -> None:
        """Execute the query and display results."""
        self.table.clear()
        self.table.columns.clear()
        try:
            self._sql = sql
            df = self.ctx.query(sql).df()
            self.app.call_from_thread(self._update_table, sql, df)
        except Exception as e:
            self.notify(f"Error executing query:\n{str(e)}", severity="error")
