from __future__ import annotations

import time

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import DataTable, Static, TabbedContent, TabPane

from lakefront.core import ProjectContext
from lakefront.tui.screens.explore import ExploreScreen


class ResultsPane(Widget):
    """Middle-bottom pane: query results in tabs."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.border_title = "Results"
        self._tab_count = 0
        self._tab_sql: dict[str, str] = {}

    BINDINGS = [
        Binding("x", "export", "Export to file", show=True),
        Binding("e", "explore", "Explore", show=True),
        Binding("ctrl+w", "close_tab", "Close tab", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Static(
            "no results yet — run a query with Ctrl+R",
            classes="meta-bar",
            id="meta-bar",
        )
        yield TabbedContent(id="tabs")

    def action_export(self) -> None:
        self.notify("export not yet implemented")

    def action_explore(self) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        active_id = tabs.active
        if not active_id or active_id not in self._tab_sql:
            self.notify("No data to explore", severity="warning")
            return
        sql = self._tab_sql[active_id]
        self.app.push_screen(ExploreScreen(self.ctx, "query", sql))

    def action_close_tab(self) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        active_id = tabs.active
        if active_id:
            self._tab_sql.pop(active_id, None)
            tabs.remove_pane(active_id)

    def _make_tab_id(self) -> str:
        self._tab_count += 1
        return f"result-{self._tab_count}"

    def _add_tab(self, tab_id: str, sql: str, df, elapsed_ms: int) -> None:
        """Add a new tab with results. Called from main thread."""
        tabs = self.query_one("#tabs", TabbedContent)

        label = f"Q{self._tab_count}"
        table = DataTable(id=f"table-{tab_id}", zebra_stripes=True)
        table.cursor_type = "row"

        pane = TabPane(label, table, id=tab_id)
        tabs.add_pane(pane)
        tabs.active = tab_id

        # Populate the table after mounting
        self.app.call_later(self._populate_table, tab_id, sql, df, elapsed_ms)

    def _populate_table(self, tab_id: str, sql: str, df, elapsed_ms: int) -> None:
        table = self.query_one(f"#table-{tab_id}", DataTable)
        if not df.empty:
            table.add_columns(*df.columns)
            table.add_rows(df.itertuples(index=False, name=None))
            self.notify(f"Query returned {len(df)} rows", severity="information")
        else:
            self.notify("Query returned no rows", severity="information")

        short_sql = sql[:50] + "..." if len(sql) > 50 else sql
        self._update_result_message(
            f"Query executed: {short_sql} in {elapsed_ms:.1f} ms"
        )

    def _update_result_message(self, message: str) -> None:
        self.query_one("#meta-bar", Static).update(message.replace("\n", " "))

    def _apply_result(
        self, sql: str, tab_id: str, df, replace: bool, elapsed_ms: int
    ) -> None:
        if replace:
            self._populate_table(tab_id, sql, df, elapsed_ms)
        else:
            self._add_tab(tab_id, sql, df, elapsed_ms)

    def _set_loading(self, tab_id: str, replace: bool) -> None:
        self._update_result_message("Running query...")
        if replace:
            try:
                table = self.query_one(f"#table-{tab_id}", DataTable)
                table.clear()
                table.columns.clear()
            except Exception:
                pass

    @work(thread=True)
    def _execute(self, sql: str, tab_id: str, replace: bool) -> None:
        self.app.call_from_thread(self._set_loading, tab_id, replace)
        try:
            t1 = time.perf_counter()
            df = self.ctx.query(sql).df()
            t2 = time.perf_counter()
            elapsed_ms = (t2 - t1) * 1000
            self.app.call_from_thread(
                self._apply_result, sql, tab_id, df, replace, elapsed_ms
            )
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")
            self.app.call_from_thread(
                self._update_result_message, "Error executing query"
            )

    def run_query(self, sql: str, new_tab: bool = False) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        active_id = tabs.active

        if new_tab or not active_id:
            tab_id = self._make_tab_id()
            self._tab_sql[tab_id] = sql
            self._execute(sql, tab_id, replace=False)
        else:
            tab_id = active_id
            self._tab_sql[tab_id] = sql
            self._execute(sql, tab_id, replace=True)
