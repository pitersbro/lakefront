from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from lakefront.core import ProjectContext


class FocusableStatic(Static):
    """A Static that can actually receive focus."""

    can_focus = True


class SourceItem(Widget):
    """A single source entry that can be expanded to show columns."""

    can_focus = True
    expanded: reactive[bool] = reactive(False)

    BINDINGS = [
        Binding("space", "toggle", "Expand/Collapse", show=True),
        Binding("j", "focus_next_row", "Next row", show=False),
        Binding("k", "focus_prev_row", "Prev row", show=False),
    ]

    DEFAULT_CSS = """
    SourceItem {
        height: auto;
    }
    SourceItem .source-row {
        padding: 0 1 0 2;
        height: 1;
        color: $text-muted;
    }
    SourceItem .column-row {
        padding: 0 1 0 4;
        height: 1;
        color: $text-disabled;
    }
    SourceItem:focus .source-row,
    SourceItem .source-row:focus,
    SourceItem .column-row:focus {
        background: $accent 20%;
        color: $text;
    }
    """

    def __init__(self, name: str, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.source_name = name
        self.ctx = ctx
        self._columns: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        arrow = "▾" if self.expanded else "▸"
        yield FocusableStatic(f"{arrow} {self.source_name}", classes="source-row")
        if self.expanded:
            if not self._columns:
                self._fetch_columns()
            for col_name, col_type in self._columns:
                yield FocusableStatic(
                    f"  {col_name}  [{col_type}]", classes="column-row"
                )

    def _fetch_columns(self):
        try:
            result = self.ctx.source_describe(self.source_name).df()
            self._columns = [
                (row["column_name"], row["column_type"]) for _, row in result.iterrows()
            ]
        except Exception as e:
            self._columns = [(f"error: {e}", "")]

    def action_toggle(self) -> None:
        self.expanded = not self.expanded
        self.refresh(recompose=True)

    def action_focus_next_row(self) -> None:
        rows = list(self.query("FocusableStatic"))
        if not rows:
            return

        focused = self.app.focused
        try:
            idx = rows.index(focused)
            next_idx = (idx + 1) % len(rows)
        except ValueError:
            next_idx = 0

        rows[next_idx].focus()

    def action_focus_prev_row(self) -> None:
        rows = list(self.query("FocusableStatic"))
        if not rows:
            return

        focused = self.app.focused
        try:
            idx = rows.index(focused)
            prev_idx = (idx - 1) % len(rows)
        except ValueError:
            prev_idx = len(rows) - 1

        rows[prev_idx].focus()


class SourcePane(Widget):
    """Left pane: lists attached data sources grouped by kind."""

    can_focus = True
    # Reactive: holds the name of the currently active source
    active_source: reactive[str | None] = reactive(None)

    BINDINGS = [
        Binding("a", "attach", "Attach source", show=True),
        Binding("d", "detach", "Detach source", show=True),
        Binding("e", "explore", "Explore", show=True),
        Binding("h", "focus_prev_source", "Prev source", show=True),
        Binding("l", "focus_next_source", "Next source", show=True),
        Binding("j", "forward_j", "Down", show=True),
        Binding("k", "forward_k", "Up", show=True),
    ]

    DEFAULT_CSS = """
    SourcePane { background: $surface; }
    SourcePane > .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }
    SourcePane .group-label {
        color: $text-disabled;
        padding: 0 1;
        height: 1;
    }
    """

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        yield Static("SOURCES", classes="pane-title")
        with VerticalScroll():
            for typ, names in self.ctx.sources_by_type().items():
                yield Static(typ.upper(), classes="group-label")
                for name in names:
                    yield SourceItem(name, self.ctx)

    # def on_focus(self) -> None:
    #     items = self.query(SourceItem)
    #     if items:
    #         items.first().focus()
    def on_focus(self) -> None:
        """When pane gains focus, activate the first source if none is set."""
        if self.active_source is None:
            items = self.query(SourceItem)
            if items:
                first = items.first()
                first.focus()
                self.active_source = first.source_name  # ← set active

    # Optional: watch the reactive and do something when it changes
    def watch_active_source(self, new_source: str | None) -> None:
        """Called automatically whenever active_source changes."""
        if new_source:
            self.notify(f"Active source → {new_source}", timeout=1.5)
            # You can also trigger other actions here, e.g. refresh right pane
        else:
            self.notify("No active source", timeout=1)

    # ── Source navigation (h / l) ──
    def action_focus_next_source(self) -> None:
        items: list[SourceItem] = list(self.query(SourceItem))
        if not items:
            return
        focused = self.app.focused
        try:
            idx = items.index(focused) if isinstance(focused, SourceItem) else -1
        except ValueError:
            idx = -1
        next_idx = (idx + 1) % len(items)
        item = items[next_idx]
        item.focus()
        self.active_source = item.source_name  # ← update active
        self.scroll_to_widget(item, animate=False)

    def action_focus_prev_source(self) -> None:
        items: list[SourceItem] = list(self.query(SourceItem))
        if not items:
            return
        focused = self.app.focused
        try:
            idx = items.index(focused) if isinstance(focused, SourceItem) else 0
        except ValueError:
            idx = 0
        prev_idx = (idx - 1) % len(items)
        item = items[prev_idx]
        item.focus()
        self.active_source = item.source_name  # ← update active
        self.scroll_to_widget(item, animate=False)

    # ── Forward j/k to current SourceItem ──
    def action_forward_j(self) -> None:
        focused = self.app.focused
        if isinstance(focused, SourceItem):
            focused.action_focus_next_row()
        else:
            self.action_focus_next_source()

    def action_forward_k(self) -> None:
        focused = self.app.focused
        if isinstance(focused, SourceItem):
            focused.action_focus_prev_row()
        else:
            self.action_focus_prev_source()

    def action_attach(self) -> None:
        self.notify("attach: not yet implemented")

    def action_detach(self) -> None:
        self.notify("detach: not yet implemented")

    def action_explore(self) -> None:
        self.notify("explore: not yet implemented")
