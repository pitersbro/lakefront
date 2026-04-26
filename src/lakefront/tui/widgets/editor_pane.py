from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.widget import Widget
from textual.widgets import TabbedContent, TabPane, TextArea

from lakefront.core import ProjectContext


class EditorPane(Widget):
    """Middle-top pane: DuckDB SQL editor with tabbed scripts."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.border_title = "SQL Editor"
        self._tab_count = 0

    BINDINGS = [
        Binding("ctrl+r", "run_query", "Run query", show=True),
        Binding("ctrl+n", "run_query_in_new_tab", "Run query in new tab", show=True),
        Binding("ctrl+s", "save_script", "Save script", show=True),
        Binding("ctrl+t", "new_tab", "New tab", show=True),
        Binding("ctrl+w", "close_tab", "Close tab", show=True),
    ]

    _PLACEHOLDER_SQL = "SELECT * FROM mycsv LIMIT 100"

    def _make_tab_id(self) -> tuple[str, str]:
        """Return (tab_id, label) for a new tab."""
        self._tab_count += 1
        return f"editor-{self._tab_count}", f"Script{self._tab_count}.sql"

    def compose(self) -> ComposeResult:
        tab_id, label = self._make_tab_id()
        with TabbedContent(id="editor-tabs"):
            with TabPane(label, id=tab_id):
                yield TextArea(
                    self._PLACEHOLDER_SQL,
                    language="sql",
                    id=f"textarea-{tab_id}",
                )

    # ── helpers ──────────────────────────────────────────────────────────────

    def _active_textarea(self) -> TextArea | None:
        """Return the TextArea in the currently active tab, or None."""
        tabs = self.query_one("#editor-tabs", TabbedContent)
        active_id = tabs.active
        if not active_id:
            return None
        try:
            return self.query_one(f"#textarea-{active_id}", TextArea)
        except Exception:
            return None

    # ── actions ──────────────────────────────────────────────────────────────

    def action_run_query(self) -> None:
        """Post the SQL from the active tab to run in ResultsPane."""
        self.notify("Running query in active tab…")
        ta = self._active_textarea()
        if ta is None:
            self.notify("No active editor tab", severity="warning")
            return
        sql = ta.text.strip()
        if not sql:
            self.notify("Editor is empty", severity="warning")
            return
        self.post_message(QueryRequested(sql, new_tab=False))

    def action_run_query_in_new_tab(self) -> None:
        ta = self._active_textarea()
        if ta is None:
            self.notify("No active editor tab", severity="warning")
            return
        sql = ta.text.strip()
        if not sql:
            self.notify("Editor is empty", severity="warning")
            return
        self.post_message(QueryRequested(sql, new_tab=True))

    def action_new_tab(self) -> None:
        tab_id, label = self._make_tab_id()
        tabs = self.query_one("#editor-tabs", TabbedContent)
        pane = TabPane(label, id=tab_id)
        tabs.add_pane(pane)
        # Mount the TextArea after the pane is in the DOM
        self.app.call_later(self._mount_textarea, tab_id)
        tabs.active = tab_id

    def _mount_textarea(self, tab_id: str) -> None:
        pane = self.query_one(f"#editor-{tab_id}", TabPane) if False else None
        # query by id directly — TabPane id matches what we passed
        try:
            pane = self.query_one(f"#{tab_id}", TabPane)
            pane.mount(
                TextArea(
                    self._PLACEHOLDER_SQL,
                    language="sql",
                    id=f"textarea-{tab_id}",
                )
            )
        except Exception as e:
            self.notify(f"Could not mount editor: {e}", severity="error")

    def action_close_tab(self) -> None:
        tabs = self.query_one("#editor-tabs", TabbedContent)
        # Always keep at least one tab open
        if tabs.tab_count <= 1:
            self.notify("Cannot close the last tab", severity="warning")
            return
        active_id = tabs.active
        if active_id:
            tabs.remove_pane(active_id)

    def action_save_script(self) -> None:
        self.notify("save script: not yet implemented")


class QueryRequested(Message):
    """Posted when the user triggers a query run."""

    def __init__(self, sql: str, new_tab: bool = False) -> None:
        super().__init__()
        self.sql = sql
        self.new_tab = new_tab
