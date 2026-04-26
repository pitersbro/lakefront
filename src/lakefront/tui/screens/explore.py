from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, MarkdownViewer, Static

from lakefront.core import LlmError, ProjectContext


class ExploreScreen(Screen):
    """Dataset explorer with LLM-powered insights."""

    BINDINGS = [
        Binding("q", "app.pop_screen", "Back", show=True),
        Binding("ctrl+r", "ask", "Ask AI", show=True),
    ]

    def __init__(
        self, ctx: ProjectContext, source_name: str, sql: str | None = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.analyzer = ctx.analyzer()
        self.source_name = source_name
        self._profile: dict | None = None
        self._insights_md = ""
        self._sql = sql

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with VerticalScroll(id="stats-pane"):
                yield Static("Loading…", id="stats-content")
            with Vertical(id="right"):
                yield Static(
                    f"✦ AI INSIGHTS  —  {self.source_name}", classes="pane-title"
                )
                with VerticalScroll(id="insights-scroll"):
                    yield MarkdownViewer(
                        "Press **Ctrl+R** or type a question below to get AI insights.",
                        id="insights-view",
                        show_table_of_contents=False,
                    )
                with Horizontal(id="question-bar"):
                    yield Input(
                        placeholder="Ask anything about this dataset… (Enter to send)",
                        id="question-input",
                    )
        yield Footer()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def on_mount(self) -> None:
        self._load_profile()

    @work(thread=True)
    def _load_profile(self) -> None:
        """Sample the source and build a statistical profile."""
        try:
            if self._sql:
                self._profile = self.analyzer.analyze_sql(self._sql)
            else:
                self._profile = self.analyzer.analyze_source(self.source_name)
            self.app.call_from_thread(self._render_stats, self._profile)
            # Auto-generate initial insights
            self._ask_llm("Give me a concise overview and highlight anything notable.")
        except Exception as e:
            self.app.call_from_thread(
                self.query_one("#stats-content", Static).update,
                f"[red]Error loading source:[/red] {e}",
            )

    def _render_stats(self, profile: dict) -> None:
        rendered = self.ctx.analyzer().render_profile(profile)
        self.query_one("#stats-content", Static).update(rendered)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "question-input" and event.value.strip():
            self._ask_llm(event.value.strip())
            event.input.clear()

    def action_ask(self) -> None:
        inp = self.query_one("#question-input", Input)
        if inp.value.strip():
            self._ask_llm(inp.value.strip())
            inp.clear()
        else:
            self._ask_llm("Give me a concise overview and highlight anything notable.")

    @work(thread=True)
    def _ask_llm(self, question: str) -> None:
        if self._profile is None:
            self.app.call_from_thread(
                self.notify, "Profile not ready yet", severity="warning"
            )
            return
        self.app.call_from_thread(self._set_insights, "_Thinking…_")
        try:
            md = self.ctx.analyzer().ask_llm(question, self._profile)
        except LlmError as e:
            self.notify(f"LLM request failed: {e}", severity="error")
            md = f"**Error:** {e}"
        self.app.call_from_thread(self._set_insights, md)

    def _set_insights(self, md: str) -> None:
        self.query_one("#insights-view", MarkdownViewer).document.update(md)
