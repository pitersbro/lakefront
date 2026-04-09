import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    TomlConfigSettingsSource,
)

LAKEFRONT_HOME = Path("~/.lakefront").expanduser()
CONFIG_DIR = LAKEFRONT_HOME / "config"
PROJECTS_DIR = LAKEFRONT_HOME / "projects"
STATE_FILE = LAKEFRONT_HOME / "state"


def get_active_profile() -> str:
    if env := os.getenv("LAKEFRONT_PROFILE"):
        return env
    if STATE_FILE.exists():
        return STATE_FILE.read_text().strip()
    return "default"


def set_active_profile(name: str) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(name)


def get_project_path(profile: str) -> Path:
    return PROJECTS_DIR / f"{profile}.toml"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class DuckDBConfig(BaseModel):
    threads: int = 4
    memory_limit: str = "2GB"


class S3Config(BaseModel):
    endpoint: str = ""
    access_key: str = Field(default="", json_schema_extra={"secret": True})
    secret_key: str = Field(default="", json_schema_extra={"secret": True})


# ---------------------------------------------------------------------------
# Toml source that strips secret fields
# ---------------------------------------------------------------------------


class SafeTomlSource(TomlConfigSettingsSource):
    def __call__(self) -> dict[str, Any]:
        data = super().__call__()
        for name, field in self.settings_cls.model_fields.items():
            extra = field.json_schema_extra or {}
            if extra.get("secret"):
                data.pop(name, None)
        return data


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


class Settings(BaseSettings):
    duckdb: DuckDBConfig = DuckDBConfig()
    s3: S3Config = S3Config()

    model_config = {
        "env_prefix": "LAKEFRONT_",
        "env_nested_delimiter": "__",
    }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        # dotenv_settings,
        # file_secret_settings,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,  # LAKEFRONT_S3__ACCESS_KEY etc.
            SafeTomlSource(settings_cls),  # profile toml, no secrets
        )


def _build_template() -> str:
    """Generate toml template from Settings model defaults."""
    lines = []

    for section, model in [("duckdb", DuckDBConfig), ("s3", S3Config)]:
        lines.append(f"[{section}]")
        for name, field in model.model_fields.items():
            extra = field.json_schema_extra or {}
            if extra.get("secret"):
                lines.append(
                    f'# {name} = ""  # via env: LAKEFRONT_{section.upper()}__{name.upper()}'
                )
            else:
                default = field.default
                value = f'"{default}"' if isinstance(default, str) else default
                lines.append(f"{name} = {value}")
        lines.append("")

    return "\n".join(lines)


PROFILE_TEMPLATE = _build_template()


def load_settings(profile: str | None = None) -> Settings:
    profile = profile or get_active_profile()
    config_file = get_project_path(profile)
    return Settings(
        _toml_file=config_file if config_file.exists() else None,
        profile=profile,
    )


class ConfigurationService:
    """Service for managing configuration profiles."""

    @classmethod
    def create_profile(cls, name: str):
        """Create a new profile with the given name."""
        profile_path = CONFIG_DIR / f"{name}.toml"
        if profile_path.exists():
            raise FileExistsError(f"Profile '{name}' already exists.")
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        profile_path.write_text(PROFILE_TEMPLATE)
        return profile_path

    @classmethod
    def list_profiles(cls) -> list[str]:
        """Discover all profiles in the config directory."""
        if not CONFIG_DIR.exists():
            return []
        return [f.stem for f in sorted(CONFIG_DIR.glob("*.toml"))]

    @classmethod
    def info(cls) -> dict[str, str]:
        """Get information about the configuration service."""
        return {
            "HOME_DIR": str(LAKEFRONT_HOME),
            "CONFIG_DIR": str(CONFIG_DIR),
            "PROJECTS_DIR": str(PROJECTS_DIR),
        }

    @classmethod
    def inspect_profile(cls, name: str | None) -> dict:
        """Inspect a profile by name."""
        name = name or get_active_profile()
        profile_path = CONFIG_DIR / f"{name}.toml"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found.")
        import tomllib

        with profile_path.open("rb") as f:
            return tomllib.load(f)

    @classmethod
    def set_active_profile(cls, name: str):
        """Set the active profile."""
        if name not in cls.list_profiles():
            raise ValueError(f"Profile '{name}' does not exist.")
        set_active_profile(name)

    @classmethod
    def get_active_profile(cls) -> str:
        """Get the name of the currently active profile."""
        return get_active_profile()

    @classmethod
    def initialize(cls):
        """Bootstrap ~/.lakefront directory structure."""
        LAKEFRONT_HOME.mkdir(parents=True, exist_ok=True)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

        if not STATE_FILE.exists():
            set_active_profile("default")

        if not cls.list_profiles():
            cls.create_profile("default")
