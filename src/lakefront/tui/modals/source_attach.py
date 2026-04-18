from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label

from lakefront import core

svc = core.ProjectConfigurationService


class SourceAttachModal(ModalScreen[dict | None]):
    """Modal that asks for Name and Path. Controlled by O (OK) and C (Cancel)."""

    BINDINGS = [
        Binding("o", "submit", "OK", show=True),
        Binding("c", "cancel", "Cancel", show=True),
        Binding("escape", "cancel", show=False),
    ]

    DEFAULT_CSS = """
    SourceAttachModal {
        align: center middle;
    }

    #modal-container {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 3 5;
    }

    Label {
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 2;
    }

    .buttons {
        margin-top: 2;
        text-align: center;
        color: $text-muted;
    }
    """

    def __init__(self, ctx: core.ProjectContext, **kwargs):
        super().__init__(**kwargs)
        self.ctx = ctx

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label("Enter Details", classes="h2")

            yield Label("Name:")
            yield Input(placeholder="Enter name...", id="name_input")

            yield Label("Path:")
            yield Input(placeholder="Enter path...", id="path_input")
            with Center():
                yield Button("OK", variant="primary", id="ok-button")

            yield Label(
                "Press [O] or click OK to submit • Escape to cancel", classes="help"
            )

    @on(Button.Pressed, "#ok-button")
    def on_ok_button(self) -> None:
        self.action_submit()

    def action_submit(self) -> None:
        """Called when user presses O (OK)"""
        name = self.query_one("#name_input", Input).value.strip()
        path = self.query_one("#path_input", Input).value.strip()

        if not name or not path:
            self.notify("Both Name and Path are required!", severity="error")
            return

        result = {"name": name, "path": path}
        self.dismiss(result)

    def action_cancel(self) -> None:
        """Called when user presses C or Escape"""
        self.dismiss(None)


# =====================================================================
# Main App
# =====================================================================
# class MyApp(App):
#     TITLE = "Name & Path Modal (Keyboard Only)"
#     BINDINGS = [("m", "show_modal", "Show Modal")]
#
#     def compose(self) -> ComposeResult:
#         yield Header()
#         yield Footer()
#         yield Label(
#             "Press 'm' to open the modal\nUse [O]K or [C]ancel inside modal",
#             classes="centered",
#         )
#
#     def action_show_modal(self) -> None:
#         self.push_screen(NamePathModal(), self.modal_callback)
#
#     def modal_callback(self, result: dict | None) -> None:
#         if result is None:
#             self.notify("Cancelled by user", severity="warning")
#         else:
#             self.notify(
#                 f"✅ Success!\n"
#                 f"Name : [bold]{result['name']}[/bold]\n"
#                 f"Path : [bold]{result['path']}[/bold]",
#                 severity="information",
#                 timeout=10,
#             )
#
#
# if __name__ == "__main__":
#     MyApp().run()
