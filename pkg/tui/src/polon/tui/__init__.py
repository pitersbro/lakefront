from textual.app import App, ComposeResult
from textual.widgets import Label


class PolonApp(App):
    def compose(self) -> ComposeResult:
        yield Label("hello from lop-tui")
