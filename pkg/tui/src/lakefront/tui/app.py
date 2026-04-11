from lakefront.core import ProjectContext
from lakefront.tui.screens.project import ProjectScreen
from textual.app import App


class LakefrontApp(App):
    def __init__(self, ctx: ProjectContext, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx

    def on_mount(self) -> None:
        self.push_screen(ProjectScreen(self.ctx))
