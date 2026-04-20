from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Static


class ConfirmModal(ModalScreen[bool]):
    """Minimal y/n confirmation dialog. Returns True on confirm, False on cancel."""

    BINDINGS = [
        Binding("y", "confirm", show=False),
        Binding("n", "cancel", show=False),
        Binding("escape", "cancel", show=False),
    ]

    DEFAULT_CSS = """
    ConfirmModal {
        align: center middle;
    }
    ConfirmModal > Vertical {
        background: $panel;
        border: round $primary;
        padding: 1 2;
        width: auto;
        height: auto;
        min-width: 40;
    }
    ConfirmModal #confirm-message {
        text-style: bold;
        padding-bottom: 1;
    }
    ConfirmModal #confirm-hint {
        color: $text-muted;
    }
    """

    def __init__(self, message: str, **kwargs):
        super().__init__(**kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self.message, id="confirm-message")
            yield Static("y  confirm    n / esc  cancel", id="confirm-hint")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
