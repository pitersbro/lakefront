import pytest
import tomllib
from textual.widgets import Label, TextArea

from lakefront import core
from lakefront.tui.app import LakefrontApp
from lakefront.tui.screens.configuration import SettingsEditorScreen
from lakefront.tui.screens.navigation import NavigationScreen

PROFILE = "testing"


@pytest.mark.asyncio
async def test_settings_editor_composes_profile():
    async with LakefrontApp().run_test() as pilot:
        await pilot.app.push_screen(SettingsEditorScreen(PROFILE))
        await pilot.pause()
        screen = pilot.app.screen
        assert isinstance(screen, SettingsEditorScreen)

        label = screen.query_one("#editor-label", Label)
        assert PROFILE in str(label.render())

        editor = screen.query_one("#editor", TextArea)
        # The editor is seeded with the profile's settings as TOML.
        assert tomllib.loads(editor.text) == core.load_settings(PROFILE).model_dump(
            mode="json", exclude={"path"}
        )


@pytest.mark.asyncio
async def test_settings_editor_edit_and_defocus():
    async with LakefrontApp().run_test() as pilot:
        await pilot.app.push_screen(SettingsEditorScreen(PROFILE))
        await pilot.pause()
        screen = pilot.app.screen
        editor = screen.query_one("#editor", TextArea)

        await pilot.press("i")
        assert editor.can_focus is True
        assert pilot.app.focused is editor

        await pilot.press("escape")
        assert editor.can_focus is False
        assert pilot.app.focused is not editor


@pytest.mark.asyncio
async def test_settings_editor_save_persists_changes():
    settings = core.load_settings(PROFILE)
    original = settings.path.read_text()
    try:
        async with LakefrontApp().run_test() as pilot:
            await pilot.app.push_screen(SettingsEditorScreen(PROFILE))
            await pilot.pause()
            screen = pilot.app.screen

            await pilot.press("ctrl+s")
            await pilot.pause()

            # Saved file round-trips back to the same validated settings.
            assert settings.path.exists()
            saved = tomllib.loads(settings.path.read_text())
            assert saved == settings.model_validate(saved).model_dump(
                mode="json", exclude={"path"}
            )
    finally:
        settings.path.write_text(original)


@pytest.mark.asyncio
async def test_settings_editor_save_reports_invalid_toml():
    settings = core.load_settings(PROFILE)
    original = settings.path.read_text()
    try:
        async with LakefrontApp().run_test() as pilot:
            await pilot.app.push_screen(SettingsEditorScreen(PROFILE))
            await pilot.pause()
            screen = pilot.app.screen
            editor = screen.query_one("#editor", TextArea)
            editor.text = "this is not = valid toml ["

            await pilot.press("ctrl+s")
            await pilot.pause()

            # Invalid input must not corrupt the on-disk profile.
            assert settings.path.read_text() == original
    finally:
        settings.path.write_text(original)


@pytest.mark.asyncio
async def test_settings_editor_back_pops_screen():
    async with LakefrontApp().run_test() as pilot:
        await pilot.pause()
        depth = len(pilot.app.screen_stack)
        await pilot.app.push_screen(SettingsEditorScreen(PROFILE))
        await pilot.pause()
        assert isinstance(pilot.app.screen, SettingsEditorScreen)

        # Defocus first so the editor doesn't swallow the "q" keypress.
        await pilot.press("escape")
        await pilot.press("q")
        await pilot.pause()
        assert len(pilot.app.screen_stack) == depth
        assert not isinstance(pilot.app.screen, SettingsEditorScreen)


@pytest.mark.asyncio
async def test_open_settings_editor_from_navigation():
    async with LakefrontApp().run_test() as pilot:
        await pilot.pause()
        await pilot.pause()  # allow the project-loading worker to finish
        screen = pilot.app.screen
        assert isinstance(screen, NavigationScreen)

        table = screen.query_one("#projects-table")
        table.focus()
        await pilot.pause()

        await pilot.press("e")
        await pilot.pause()

        editor = pilot.app.screen
        assert isinstance(editor, SettingsEditorScreen)
        # The profile shown matches the selected project's row.
        expected_profile = table.get_row_at(table.cursor_row)[4]
        assert editor.profile == expected_profile
