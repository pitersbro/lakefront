from textual.app import App
from textual.binding import Binding

from lakefront.core import ProjectContext, get_version, lakefront_settings
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
        self.theme = self._resolve_theme(ctx)

    def _resolve_theme(self, ctx: ProjectContext | None) -> str:
        if ctx is not None:
            settings = ctx.settings
            theme = settings.core.theme
        else:
            settings = lakefront_settings()
            theme = settings.app.theme
        if theme not in self.available_themes.keys():
            self.notify(
                f"Theme '{theme}' not found. Falling back to default theme '{DEFAULT_THEME}'.",
                severity="warning",
            )
            return DEFAULT_THEME
        return theme

    def on_mount(self) -> None:
        if self.ctx is not None:
            self.push_screen(ProjectScreen(self.ctx))
        else:
            from lakefront.tui.screens.navigation import NavigationScreen

            self.push_screen(NavigationScreen())
