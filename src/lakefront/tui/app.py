from textual.app import App
from textual.binding import Binding

from lakefront.core import ProjectContext, get_version
from lakefront.tui.screens.project import ProjectScreen

DEFAULT_THEME = "tokyo-night"


class LakefrontApp(App):
    TITLE = "Lakefront"
    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("tab", "focus_next", show=False),
        Binding("shift+tab", "focus_previous", show=False),
    ]

    def __init__(self, ctx: ProjectContext | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.ctx = ctx
        self.sub_title = f"Lakehouse Observability Platform - v{get_version()}"
        if ctx is not None:
            _theme = ctx.settings.core.theme
            if _theme not in self.available_themes.keys():
                self.theme = DEFAULT_THEME
                self.notify(
                    f"Theme '{_theme} not found. Falling back to default theme '{DEFAULT_THEME}'.",
                    severity="warning",
                )
            else:
                self.theme = _theme
        else:
            self.theme = DEFAULT_THEME

    def on_mount(self) -> None:
        if self.ctx is not None:
            self.push_screen(ProjectScreen(self.ctx))
        else:
            from lakefront.tui.screens.navigation import NavigationScreen

            self.push_screen(NavigationScreen())
