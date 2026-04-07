from lakefront.core import ProjectManager
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

pm = ProjectManager()


class NewProjectScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="project name")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted):
        pm.create(event.value)
        self.app.pop_screen()


class ProjectView(Screen):
    BINDINGS = [
        Binding("backspace", "app.pop_screen", "Back"),
        Binding("ctrl+r", "run_sql", "Run SQL"),
    ]

    CSS = """
    #left  { width: 25%; border-right: solid #39ff14 20%; }
    #main  { width: 1fr; }
    #right { width: 25%; border-left: solid #39ff14 20%; }

    #sources-list { height: 1fr; }
    #stats-panel  { height: 12; padding: 1; }

    #sql-input  { height: 3; }
    #data-table { height: 1fr; }

    Label {
        color: #39ff14;
        padding: 0 1;
    }
    """

    def __init__(self, project_name: str, **kwargs):
        super().__init__(**kwargs)
        self.project_name = project_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left"):
                yield Label("sources")
                yield ProjectListView(id="sources-list")
                yield Label("statistics")
                yield Static(id="stats-panel")
            with Vertical(id="main"):
                yield Input(placeholder="SELECT * FROM data LIMIT 100", id="sql-input")
                yield DataTable(id="data-table")
            with Vertical(id="right"):
                yield Label("schema")
                yield DataTable(id="schema-table")
        yield Footer()

    def on_list_view_selected(self, event): ...

    def action_run_sql(self): ...


class ConfirmScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(self.message)
        yield Button("Yes", id="yes", variant="error")
        yield Button("No", id="no")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed):
        self.dismiss(event.button.id == "yes")


LOGO = r"""
__________               __    
\______   \ ____ _____  |  | __
 |     ___// __ \\__  \ |  |/ /
 |    |   \  ___/ / __ \|    < 
 |____|    \___  /____  /__|_ \
               \/     \/     \/
lakehouse observability platform
"""


class ProjectListView(ListView):
    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]


class SplashScreen(Screen):
    CSS = """
        .hidden { display: none; }
        SplashScreen ListView {
            width: 40;
            height: auto;
            align: center middle;
        }
        SplashScreen #center {
            width: 40;
            height: auto;
            align: center middle;
        }
        SplashScreen {
            align: center middle;
        }

        SplashScreen Label {
            width: 40;
            content-align: center middle;
        }
        #logo {
            color: #39ff14;
            content-align: center middle;
            width: 100%;
        }

    """
    BINDINGS = [
        Binding("n", "new_project", "New"),
        Binding("d", "delete_project", "Delete"),
        Binding("enter", "open_project", "Open"),
    ]

    def action_cursor_down(self):
        self.query_one(ListView).action_scroll_down()

    def action_cursor_up(self):
        self.query_one(ListView).action_scroll_up()

    def on_mount(self):
        lv = self.query_one(ListView)
        lv.clear()
        for project in pm.list():
            lv.append(ListItem(Label(project.name)))
        lv.focus()

    def on_screen_resume(self):
        self.on_mount()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(LOGO, id="logo")
        yield Center(
            Label("Projects"),
            ProjectListView(),
            Input(placeholder="delete? y/N", id="confirm", classes="hidden"),
        )
        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected):
        name = str(event.item.query_one(Label).render())
        self.app.push_screen(ProjectView(name))

    def action_new_project(self):
        self.app.push_screen(NewProjectScreen())

    def on_input_submitted(self, event: Input.Submitted):
        confirm = self.query_one("#confirm", Input)
        confirm.add_class("hidden")
        if event.value.lower() == "y" and self._pending_delete:
            pm.delete(self._pending_delete)
            self._pending_delete = None
            self.on_mount()  # refresh list
        confirm.clear()
        self.query_one(ListView).focus()

    def action_delete_project(self):
        lv = self.query_one(ListView)
        if lv.highlighted_child:
            self._pending_delete = str(lv.highlighted_child.query_one(Label).render())
            confirm = self.query_one("#confirm", Input)
            confirm.remove_class("hidden")
            confirm.focus()


class LakeFrontApp(App):
    TITLE = "Lakehouse Observability Platform"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    CSS = """
    ListItem > ListItem.--highlight {
        background: #39ff14 20%;
    }

    ListItem > ListItem.--highlight > Label {
        color: #39ff14;
    }
    """

    def on_mount(self):
        self.push_screen(SplashScreen())
