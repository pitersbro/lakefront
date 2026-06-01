from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from lakefront import core
from lakefront.tui.screens.configuration import SettingsEditorScreen


class NavTable(DataTable):
    BINDINGS = [
        *DataTable.BINDINGS,
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]


class NavigationScreen(Screen):
    """Main navigation screen — list all projects and select one to open."""

    BINDINGS = [
        Binding("q", "app.exit", "Quit", show=True),
        Binding("e", "edit_profile", "Edit Configuration", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="nav-body"):
            with Vertical(id="nav-container"):
                yield Static("PROJECTS", id="nav-title")
                yield NavTable(id="projects-table", cursor_type="row")
        yield Footer()

    def on_mount(self) -> None:
        self._load_projects()

    def action_edit_profile(self):
        table = self.query_one("#projects-table", NavTable)
        profile = table.get_row_at(table.cursor_row)[4]
        self.app.push_screen(SettingsEditorScreen(profile))

    @work(thread=True)
    def _load_projects(self) -> None:
        names = core.list_projects()
        if not names:
            self.app.call_from_thread(self._show_empty)
            return
        rows = []
        for name in names:
            try:
                project = core.ProjectConfigurationService.get(name)
                updated = project.updated_at.strftime("%Y-%m-%d")
                description = project.description or "—"
                sources = str(len(project.sources))
                profile = project.profile
            except Exception:
                updated = "—"
                description = "error loading project"
                sources = "—"
                profile = "—"
            rows.append((name, description, sources, updated, profile))
        self.app.call_from_thread(self._populate_table, rows)

    def _show_empty(self) -> None:
        table = self.query_one("#projects-table", DataTable)
        table.remove()
        self.query_one("#nav-container", Vertical).mount(
            Static(
                "No projects found.\n\n"
                "Run [bold]lakefront projects create <name>[/bold] to create one,\n"
                "or [bold]lakefront demo[/bold] to launch the built-in demo.",
                id="nav-empty",
                markup=True,
            )
        )

    def _populate_table(self, rows: list[tuple]) -> None:
        table = self.query_one("#projects-table", NavTable)
        table.add_columns("Project", "Description", "Sources", "Updated", "Profile")
        for row in rows:
            table.add_row(*row, key=row[0])
        table.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._open_project(str(event.row_key.value))

    @work(thread=True)
    def _open_project(self, name: str) -> None:
        from lakefront.tui.screens.project import ProjectScreen

        try:
            ctx = core.get_project(name)
        except core.ProjectNotFoundError:
            self.app.call_from_thread(
                self.notify, f"Project '{name}' not found.", severity="error"
            )
            return
        try:
            self.app.call_from_thread(self.app.push_screen, ProjectScreen(ctx))
        except Exception as e:
            self.app.call_from_thread(
                self.notify, f"Error opening project: {e}", severity="error"
            )
