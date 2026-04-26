from textual.app import App
from textual.binding import Binding

from lakefront.core import ProjectContext, get_version
from lakefront.tui.screens.project import ProjectScreen


class LakefrontApp(App):
    TITLE = "Lakefront"
    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("tab", "focus_next", show=False),
        Binding("shift+tab", "focus_previous", show=False),
    ]

    def __init__(self, ctx: ProjectContext, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self.sub_title = f"Lakehouse Observability Platform - v{get_version()}"

    def on_mount(self) -> None:
        self.push_screen(ProjectScreen(self.ctx))
