from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import TextArea

from lakefront.core import ProjectContext


class EditorPane(Widget):
    """Middle-top pane: DuckDB SQL editor."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.border_title = "SQL Editor"

    BINDINGS = [
        Binding("ctrl+r", "run_query", "Run query", show=True),
        Binding("ctrl+s", "save_script", "Save script", show=True),
    ]

    _PLACEHOLDER_SQL = "SELECT * FROM mycsv LIMIT 100"

    def compose(self) -> ComposeResult:
        yield TextArea(
            self._PLACEHOLDER_SQL,
            language="sql",
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
