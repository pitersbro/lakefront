from __future__ import annotations

from lakefront.core import ProjectContext
from textual.app import ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static


class SourcePane(Widget):
    """Left pane: lists attached data sources grouped by kind."""

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    BINDINGS = [
        Binding("a", "attach", "Attach source", show=True),
        Binding("d", "detach", "Detach source", show=True),
        Binding("e", "explore", "Explore", show=True),
        Binding("enter", "open", "Open", show=True),
    ]

    DEFAULT_CSS = """
    SourcePane {
        background: $surface;
    }

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

    SourcePane ListView {
        background: $surface;
        border: none;
        height: auto;
        padding: 0;
    }

    SourcePane ListItem {
        padding: 0 1 0 2;
        height: 1;
        color: $text-muted;
    }

    SourcePane ListItem:hover {
        background: $boost;
        color: $text;
    }

    SourcePane ListItem.--highlight {
        background: $accent 20%;
        color: $text;
    }

    SourcePane .kind-badge {
        color: $warning;
    }
    """

    # Placeholder — wire up ProjectContext.sources in a later step
    _sources: list[dict] = [
        {"name": "orders", "kind": "parquet"},
        {"name": "customers", "kind": "parquet"},
        {"name": "products", "kind": "parquet"},
        {"name": "events_log", "kind": "delta"},
        {"name": "revenue_mv", "kind": "view"},
    ]

    def compose(self) -> ComposeResult:
        yield Static("SOURCES", classes="pane-title")

        groups: dict[str, list[str]] = {}
        for src in self._sources:
            groups.setdefault(src["kind"], []).append(src["name"])

        for kind, names in groups.items():
            yield Static(kind, classes="group-label")
            with ListView():
                for name in names:
                    yield ListItem(Label(f"▸ {name}"))

    def action_attach(self) -> None:
        self.notify("attach: not yet implemented")

    def action_detach(self) -> None:
        self.notify("detach: not yet implemented")

    def action_explore(self) -> None:
        self.notify("explore: not yet implemented")

    def action_open(self) -> None:
        self.notify("open: not yet implemented")
