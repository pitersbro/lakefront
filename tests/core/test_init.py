from lakefront.core.config import LAKEFRONT_HOME


def test_lakefront_settings_toml_exists():
    settings_path = LAKEFRONT_HOME / "settings.toml"
    assert settings_path.exists(), f"Expected settings.toml to exist at {settings_path}"


def test_lakefront_settings_loads():
    from lakefront.core import lakefront_settings

    settings = lakefront_settings()
    assert settings is not None, (
        "Expected lakefront_settings() to return a settings object"
    )
    assert settings.app.theme == "tokyo-night"


def test_lakefront_settings_env_override(monkeypatch):
    monkeypatch.setenv("LAKEFRONT_APP__THEME", "dracula")

    from lakefront.core import lakefront_settings

    settings = lakefront_settings()
    assert settings.app.theme == "dracula", (
        "Expected environment variable to override settings.toml value"
    )
