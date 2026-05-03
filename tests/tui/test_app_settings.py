from lakefront import core
from lakefront.tui.app import LakefrontApp


def test_theme_resolution_with_context(ctx):
    app = LakefrontApp(ctx)
    assert app._resolve_theme(ctx) == ctx.settings.core.theme


def test_theme_resolution_without_context():
    app = LakefrontApp()
    settings = core.lakefront_settings()
    expected_theme = (
        settings.app.theme
        if settings.app.theme in app.available_themes
        else "tokyo-night"
    )
    assert app._resolve_theme(None) == expected_theme


def test_theme_resolution_with_invalid_theme():
    class MockSettings:
        class CoreSettings:
            theme = "nonexistent-theme"

        core = CoreSettings()

    app = LakefrontApp()
    result = app._resolve_theme(None)
    assert result == "tokyo-night"
