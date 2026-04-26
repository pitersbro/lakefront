from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from lakefront import core
from lakefront.tui.modals.confirm import ConfirmModal
from lakefront.tui.modals.source_attach import SourceAttachModal

svc = core.ProjectConfigurationService


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

    def __init__(self, name: str, ctx: core.ProjectContext, **kwargs):
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

    def __init__(self, ctx: core.ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.border_title = "Sources"

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            for typ, names in self.ctx.sources_by_type().items():
                yield Static(typ.upper(), classes="group-label")
                for name in names:
                    yield SourceItem(name, self.ctx)

    def on_focus(self) -> None:
        """When pane gains focus, activate the first source if none is set."""
        if self.active_source is None:
            items = self.query(SourceItem)
            if items:
                first = items.first()
                first.focus()
                self.active_source = first.source_name

    def watch_active_source(self, new_source: str | None) -> None:
        """Called automatically whenever active_source changes."""
        if new_source:
            self.notify(f"Active source → {new_source}", timeout=1.5)
        else:
            self.notify("No active source", timeout=1)

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
        self.active_source = item.source_name
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
        self.active_source = item.source_name
        self.scroll_to_widget(item, animate=False)

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
        self.app.push_screen(SourceAttachModal(self.ctx), self.modal_callback)

    def modal_callback(self, result: dict | None) -> None:
        if result is None:
            self.notify("Cancelled", severity="warning")
        else:
            name, path = result["name"], result["path"]
            self.ctx.source_attach(name=name, path=path, kind="local")
            self.ctx = self.ctx.reinitialize()  # ← reload context to include new source
            self._rebuild_sources()
            self.notify(
                f"✅ Received:\n"
                f"Name: [bold]{result['name']}[/bold]\n"
                f"Path: [bold]{result['path']}[/bold]",
                severity="information",
                timeout=8,
            )

    def _rebuild_sources(self) -> None:
        scroll = self.query_one(VerticalScroll)
        scroll.remove_children()
        for typ, names in self.ctx.sources_by_type().items():
            scroll.mount(Static(typ.upper(), classes="group-label"))
            for n in names:
                scroll.mount(SourceItem(n, self.ctx))

    def action_detach(self) -> None:
        if self.active_source is None:
            self.notify("No active source to detach", severity="warning")
            return

        name = self.active_source

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            self.ctx.source_detach(name=name)
            self.ctx = self.ctx.reinitialize()
            self.active_source = None
            self._rebuild_sources()
            self.notify(f"🗑️ Detached [bold]{name}[/bold]", timeout=4)

        self.app.push_screen(ConfirmModal(f"Detach '{name}'?"), on_confirm)

    def action_explore(self) -> None:
        if self.active_source is None:
            self.notify("Select a source first", severity="warning")
            return
        from lakefront.tui.screens.explore import ExploreScreen

        self.app.push_screen(ExploreScreen(self.ctx, self.active_source))
