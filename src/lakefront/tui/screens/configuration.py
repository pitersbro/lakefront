from __future__ import annotations

import tomli_w
import tomllib
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Label, TextArea

from lakefront import core


class SettingsEditorScreen(Screen):
    can_focus = True
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("escape", "defocus", "Normal mode"),
        Binding("q", "app.pop_screen", "Back"),
        Binding("i", "edit", "Edit"),
    ]

    def __init__(self, profile: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.profile = profile
        model = core.load_settings(profile)
        self.model = model
        self.path = model.path

    def compose(self) -> ComposeResult:
        yield Label(f"Configuration profile editor - {self.profile}", id="editor-label")
        yield TextArea(
            tomli_w.dumps(self.model.model_dump()),
            language="toml",
            id="editor",
        )

        yield Footer()

    def on_mount(self):
        self.set_focus(None)

    def action_defocus(self) -> None:
        ta = self.query_one("#editor")
        ta.can_focus = False
        self.set_focus(None)
        self.focus()

    def action_edit(self):
        ta = self.query_one("#editor")
        ta.can_focus = True
        ta.focus()

    def action_save(self) -> None:
        text = self.query_one("#editor", TextArea).text
        try:
            data = tomllib.loads(text)
            validated = self.model.__class__.model_validate(data)
            self.path.write_text(tomli_w.dumps(validated.model_dump()))
            self.notify(f"Configuration saved {self.path}")
        except Exception as e:
            self.notify(str(e), severity="error")
