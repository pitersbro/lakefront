from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from lakefront import core


class NavigationScreen(Screen):
    """Main navigation screen — list all projects and select one to open."""

    BINDINGS = [
        Binding("q", "app.exit", "Quit", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._project_names = core.list_projects()

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="nav-body"):
            with Vertical(id="nav-container"):
                yield Static("PROJECTS", id="nav-title")
                if self._project_names:
                    yield DataTable(id="projects-table", cursor_type="row")
                else:
                    yield Static(
                        "No projects found.\n\n"
                        "Run [bold]lakefront projects create <name>[/bold] to create one,\n"
                        "or [bold]lakefront demo[/bold] to launch the built-in demo.",
                        id="nav-empty",
                        markup=True,
                    )
        yield Footer()

    def on_mount(self) -> None:
        if not self._project_names:
            return
        table = self.query_one("#projects-table", DataTable)
        table.add_columns("Project", "Description", "Sources", "Updated")
        for name in self._project_names:
            try:
                project = core.ProjectConfigurationService.get(name)
                updated = project.updated_at.strftime("%Y-%m-%d")
                description = project.description or "—"
                sources = str(len(project.sources))
            except Exception:
                updated = "—"
                description = "error loading project"
                sources = "—"
            table.add_row(name, description, sources, updated, key=name)
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open_project(str(event.row_key.value))

    def _open_project(self, name: str) -> None:
        from lakefront.tui.screens.project import ProjectScreen

        try:
            ctx = core.get_project(name)
        except core.ProjectNotFoundError:
            self.notify(f"Project '{name}' not found.", severity="error")
            return
        try:
            self.app.push_screen(ProjectScreen(ctx))
        except Exception as e:
            self.notify(f"Error opening project: {e}", severity="error")
