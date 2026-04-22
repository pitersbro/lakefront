from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from lakefront.core import ProjectContext

from .source_pane import SourcePane


class ProfilerPane(Widget):
    """Right pane: summary statistics for the active source or result."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    DEFAULT_CSS = """
    ProfilerPane {
        background: $surface;
        padding: 0;
    }

    ProfilerPane > .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }

    ProfilerPane .stat-label {
        color: $text-disabled;
        padding: 0 1;
        height: 1;
    }

    ProfilerPane .stat-value {
        color: $text;
        padding: 0 2;
        height: 1;
        text-style: bold;
    }

    ProfilerPane .stat-sub {
        color: $text-muted;
        padding: 0 2;
        height: 1;
    }

    ProfilerPane .divider {
        color: $panel;
        height: 1;
        padding: 0 1;
    }


    #profiler-container {
        width: 40;
        height: 100%;
        border-right: tall $panel;
        overflow-y: auto;
    }
    .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }


    """

    def on_focus(self) -> None:
        self.query_one("#profiler-container", VerticalScroll).focus()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="profiler-container", can_focus=True):
            yield Static("PROFILE", classes="pane-title")
            yield Static("Loading…", id="profiler-content")

    def on_mount(self) -> None:
        source_pane = self.screen.query_one(SourcePane)
        self.watch(source_pane, "active_source", self._load_profile)

        if source_pane.active_source is not None:
            self._load_profile(source_pane.active_source)

    @work(thread=True)
    def _load_profile(self, source_name: str) -> None:
        """Sample the source and build a statistical profile."""
        try:
            self._profile = self.ctx.analyzer().analyze_source(source_name)
            self.app.call_from_thread(self._render_stats, self._profile)
        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#profiler-content", Static).update,
                f"[red]Error loading source data profile:[/red] {e}",
            )

    def _render_stats(self, profile: dict) -> None:
        rendered = self.ctx.analyzer().render_profile(profile)
        self.query_one("#profiler-content", Static).update(rendered)
