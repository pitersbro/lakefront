from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static, TextArea

from lakefront.core import ProjectContext


class EditorPane(Widget):
    """Middle-top pane: DuckDB SQL editor."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    BINDINGS = [
        Binding("ctrl+r", "run_query", "Run query", show=True),
        Binding("ctrl+s", "save_script", "Save script", show=True),
    ]

    DEFAULT_CSS = """
    EditorPane {
        background: $surface;
    }

    EditorPane > .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }

    EditorPane TextArea {
        height: 1fr;
        border: none;
        background: $surface;
    }
    """

    _PLACEHOLDER_SQL = (
        "-- query orders, last 30 days\n"
        "SELECT order_id, customer_id, SUM(amount) AS total,\n"
        "       status, created_at\n"
        "FROM   orders\n"
        "WHERE  created_at >= now() - INTERVAL '30 days'\n"
        "GROUP BY 1, 2, 4, 5\n"
        "LIMIT  1000;"
    )
    _PLACEHOLDER_SQL = "select * from mycsv"

    def compose(self) -> ComposeResult:
        yield Static("SQL EDITOR", classes="pane-title")
        yield TextArea(
            self._PLACEHOLDER_SQL,
            language="sql",
            theme="monokai",
            id="sql-editor",
        )

    def action_run_query(self) -> None:
        sql = self.query_one("#sql-editor", TextArea).text
        self.post_message(QueryRequested(sql))

    def action_save_script(self) -> None:
        self.notify("save script: not yet implemented")


class QueryRequested(Message):
    """Posted when the user triggers a query run."""

    def __init__(self, sql: str) -> None:
        super().__init__()
        self.sql = sql
