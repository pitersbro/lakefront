from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Static

from lakefront.core import ProjectContext


class ProfilerPane(Widget):
    """Right pane: summary statistics for the active source or result."""

    can_focus = True

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.border_title = "Summary"
        self._generation = 0

    def on_focus(self) -> None:
        self.query_one("#profiler-container", VerticalScroll).focus()

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="profiler-container", can_focus=True):
            yield Static(
                "Press [bold]p[/bold] on a source to load its profile.",
                id="profiler-content",
                markup=True,
            )

    @work(thread=True)
    def _load_profile(self, source_name: str) -> None:
        # Each call claims a new generation. If the user triggers profiling quickly,
        # multiple workers run concurrently. Only the worker whose generation still
        # matches _generation when it finishes is the latest request — all earlier
        # ones discard their results instead of updating the UI with stale data.
        self._generation += 1
        generation = self._generation
        try:
            profile = self.ctx.analyzer().analyze_source(source_name)
            if generation != self._generation:
                return
            self.app.call_from_thread(self._render_stats, profile)
        except Exception as e:
            if generation != self._generation:
                return
            self.app.call_from_thread(
                self.query_one("#profiler-content", Static).update,
                f"[red]Error loading source data profile:[/red] {e}",
            )

    def _render_stats(self, profile: dict) -> None:
        rendered = self.ctx.analyzer().render_profile(profile)
        self.query_one("#profiler-content", Static).update(rendered)
