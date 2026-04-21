from __future__ import annotations

import json

import httpx
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, MarkdownViewer, Static

from lakefront.core import ProjectContext

SYSTEM_PROMPT = """\
You are a senior data analyst. You receive a statistical profile of a dataset
and the user's question. Provide clear, concise, actionable insights.
Use markdown with headers and bullet points. Be specific — reference actual
column names, values and numbers from the profile.
"""


class ExploreScreen(Screen):
    """Dataset explorer with LLM-powered insights."""

    BINDINGS = [
        Binding("q", "app.pop_screen", "Back", show=True),
        Binding("ctrl+r", "ask", "Ask AI", show=True),
    ]

    CSS = """
    ExploreScreen { layout: vertical; }

    #body {
        layout: horizontal;
        height: 1fr;
    }

    #stats-pane {
        width: 40;
        height: 100%;
        border-right: tall $panel;
        overflow-y: auto;
    }

    #right {
        layout: vertical;
        width: 1fr;
        height: 100%;
    }

    #insights-scroll {
        height: 1fr;
        padding: 1 2;
    }

    #question-bar {
        height: 3;
        padding: 0 1;
        border-top: tall $panel;
    }

    .pane-title {
        background: $panel;
        color: $text-muted;
        padding: 0 1;
        text-style: bold;
        height: 1;
    }

    .stat-section { color: $text-disabled; padding: 0 1; height: 1; }
    .stat-row     { color: $text;         padding: 0 2; height: 1; }
    .stat-sep     { color: $panel;        padding: 0 1; height: 1; }
    """

    def __init__(self, ctx: ProjectContext, source_name: str, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx
        self.analyzer = ctx.analyzer()
        self.source_name = source_name
        self._profile: dict | None = None
        self._insights_md = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="body"):
            with VerticalScroll(id="stats-pane"):
                yield Static("PROFILE", classes="pane-title")
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
        lines: list[str] = [
            f"[bold]Rows:[/bold]    {profile['rows']:,}",
            f"[bold]Columns:[/bold] {profile['columns']}",
            "─" * 36,
        ]
        for col, meta in profile["schema"].items():
            lines.append(f"[bold]{col}[/bold]")
            lines.append(f"  type:  {meta['type']}")
            lines.append(f"  nulls: {meta['null_pct']}%")
            stats = profile["stats"].get(col, {})
            if "mean" in stats:
                lines.append(f"  min/max: {stats['min']} / {stats['max']}")
                lines.append(f"  mean: {stats['mean']}  median: {stats['median']}")
            elif "unique" in stats:
                lines.append(f"  unique: {stats['unique']}")
                top = ", ".join(
                    f"{k}({v})" for k, v in list(stats["top_values"].items())[:3]
                )
                lines.append(f"  top: {top}")
            lines.append("─" * 36)

        self.query_one("#stats-content", Static).update("\n".join(lines))

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

        profile_json = json.dumps(self._profile, indent=2, default=str)
        user_msg = (
            f"Dataset profile:\n```json\n{profile_json}\n```\n\nQuestion: {question}"
        )

        try:
            response = httpx.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.ctx.settings.anthropic.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1024,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_msg}],
                },
                timeout=60,
            )
            data = response.json()
            if response.status_code != 200:
                self.notify(f"{response.reason_phrase}\n{str(data)}", severity="error")
            md = data["content"][0]["text"].strip()
        except Exception as e:
            md = f"**Error:** {e}"

        self.app.call_from_thread(self._set_insights, md)

    def _set_insights(self, md: str) -> None:
        self.query_one("#insights-view", MarkdownViewer).document.update(md)
