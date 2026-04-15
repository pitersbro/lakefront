from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from lakefront.core import ProjectContext
from lakefront.tui.widgets.editor_pane import EditorPane, QueryRequested
from lakefront.tui.widgets.profiler_pane import ProfilerPane
from lakefront.tui.widgets.results_pane import ResultsPane
from lakefront.tui.widgets.source_pane import SourcePane


class ProjectScreen(Screen):
    """Three-pane project screen: sources | editor+results | profiler."""

    def __init__(self, ctx: ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    BINDINGS = [
        # Binding("tab", "cycle_pane", "Switch pane", show=True),
        Binding("q", "app.pop_screen", "Back", show=True),
    ]

    CSS = """
    ProjectScreen {
        layout: vertical;
    }

    #body {
        layout: horizontal;
        height: 1fr;
    }

    SourcePane {
        width: 24;
        height: 100%;
        border-right: tall $panel;
    }

    #center {
        layout: vertical;
        width: 1fr;
        height: 100%;
    }

    EditorPane {
        height: 12;
        border-bottom: tall $panel;
    }

    ResultsPane {
        height: 1fr;
    }

    ProfilerPane {
        width: 26;
        height: 100%;
        border-left: tall $panel;
    }
    """

    # PANES = ["source-pane", "editor-pane", "results-pane", "profiler-pane"]
    # _focus_index: int = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            yield SourcePane(self.ctx, id="source-pane")
            with Vertical(id="center"):
                yield EditorPane(self.ctx, id="editor-pane")
                yield ResultsPane(self.ctx, id="results-pane")
            yield ProfilerPane(self.ctx, id="profiler-pane")
        yield Footer()

    # ── THIS IS THE KEY FIX ──
    def on_query_requested(self, message: QueryRequested) -> None:
        """Receive query from EditorPane and forward it to ResultsPane."""
        try:
            results_pane = self.query_one("#results-pane", ResultsPane)
            results_pane.run_query(message.sql)
        except Exception as e:
            self.notify(f"Could not run query: {e}", severity="error")

    # def action_cycle_pane(self) -> None:
    #     self._focus_index = (self._focus_index + 1) % len(self.PANES)
    #     widget = self.query_one(f"#{self.PANES[self._focus_index]}")
    #     widget.focus()
