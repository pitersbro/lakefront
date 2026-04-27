from __future__ import annotations

import os
from pathlib import Path

import tomli_w
import tomllib
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from lakefront import models, util

from .exceptions import (
    ProjectExistsError,
    ProjectNotFoundError,
    SourceExistsError,
    SourceNotFoundError,
)


def get_env_var(name: str, default: str | None = None) -> Path:
    """Get an environment variable with an optional default."""
    envvar = os.getenv(name)
    if envvar:
        return Path(envvar).expanduser()
    if default:
        return Path(default).expanduser()
    raise EnvironmentError(
        f"Environment variable '{name}' is not set and no default provided."
    )


LAKEFRONT_HOME = get_env_var("LAKEFRONT_HOME", "~/.lakefront")
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


class TomlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls, toml_path: Path):
        super().__init__(settings_cls)
        with toml_path.open("rb") as f:
            self._data = tomllib.load(f)

    def get_field_value(self, field, field_name):
        return self._data.get(field_name), field_name, False

    def __call__(self):
        return self._data


class Settings(BaseSettings):
    core: models.CoreConfig = models.CoreConfig()
    duckdb: models.DuckDBConfig = models.DuckDBConfig()
    s3: models.S3Config = models.S3Config()
    anthropic: models.AnthropicConfig = models.AnthropicConfig()
    path: Path | None = Field(default=None, exclude=True)

    model_config = {
        "env_prefix": "LAKEFRONT_",
        "env_nested_delimiter": "__",
        "extra": "allow",
    }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Customise the settings sources to include a TOML file source if a path is provided.
        Final resolution order (highest to lowest precedence):

        1. Initialization kwargs
        2. Environment variables
        3. .env file
        4. TOML file at the provided path

        """
        toml_path = init_settings.init_kwargs.get("path")
        if toml_path:
            toml_source = TomlConfigSettingsSource(settings_cls, Path(toml_path))
            return init_settings, env_settings, dotenv_settings, toml_source
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    @classmethod
    def from_file(cls, file_path: Path) -> Settings:
        return cls(path=file_path)


def _build_template() -> str:
    """Generate toml template from Settings model defaults."""
    lines = []

    for section, model in [
        ("core", models.CoreConfig),
        ("duckdb", models.DuckDBConfig),
        ("s3", models.S3Config),
        ("anthropic", models.AnthropicConfig),
    ]:
        lines.append(f"[{section}]")
        for name, field in model.model_fields.items():
            extra = field.json_schema_extra or {}
            if extra.get("secret"):
                lines.append(
                    f'{name} = ""  # via env: LAKEFRONT_{section.upper()}__{name.upper()}'
                )
            else:
                default = field.default
                if isinstance(default, bool):
                    value = "true" if default else "false"
                elif isinstance(default, str):
                    value = f'"{default}"'
                else:
                    value = default
                lines.append(f"{name} = {value}")
        lines.append("")

    return "\n".join(lines)


PROFILE_TEMPLATE = _build_template()


def load_settings(profile: str | None = None) -> Settings:
    profile = profile or get_active_profile()
    config_file = CONFIG_DIR / f"{profile}.toml"
    if config_file.exists():
        return Settings.from_file(config_file)
    raise FileNotFoundError(f"Profile '{profile}' not found at {config_file}.")


class ProfileConfigurationService:
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
    def home_dir(cls) -> Path:
        """Get the home directory for lakefront configuration."""
        return LAKEFRONT_HOME

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
    def delete_profile(cls, name: str) -> None:
        """Delete a profile by name."""
        profile_path = CONFIG_DIR / f"{name}.toml"
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found.")
        profile_path.unlink()

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


def initialize():
    """Bootstrap ~/.lakefront directory structure."""
    LAKEFRONT_HOME.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

    if not STATE_FILE.exists():
        set_active_profile("default")

    if not ProfileConfigurationService.list_profiles():
        ProfileConfigurationService.create_profile("default")


class ProjectConfigurationService:
    @classmethod
    def _path(cls, name: str) -> Path:
        return PROJECTS_DIR / name / "project.toml"

    @classmethod
    def create(
        cls, name: str, description: str = "", profile: str = "default"
    ) -> models.Project:
        project_dir = PROJECTS_DIR / name
        if project_dir.exists():
            raise ProjectExistsError(f"Project '{name}' already exists.")

        project_dir.mkdir(parents=True)
        # TODO: Think about it
        # (project_dir / "results").mkdir()

        project = models.Project(name=name, description=description, profile=profile)
        cls._save(project)
        return project

    @classmethod
    def get(cls, name: str) -> models.Project:
        path = cls._path(name)
        if not path.exists():
            raise ProjectNotFoundError(f"Project '{name}' not found.")
        import tomllib

        with path.open("rb") as f:
            return models.Project(**tomllib.load(f))

    @classmethod
    def list_projects(cls) -> list[str]:
        """List all project names."""
        if not PROJECTS_DIR.exists():
            return []
        return sorted(
            p.name
            for p in sorted(PROJECTS_DIR.iterdir())
            if p.is_dir() and (p / "project.toml").exists()
        )

    @classmethod
    def delete(cls, name: str) -> None:
        project_dir = PROJECTS_DIR / name
        if not project_dir.exists():
            raise ProjectNotFoundError(f"Project '{name}' not found.")
        import shutil

        shutil.rmtree(project_dir)

    @classmethod
    def add_source(cls, name: str, source: models.DataSource) -> models.Project:
        project = cls.get(name)
        if any(s.name == source.name for s in project.sources):
            raise SourceExistsError(
                f"Source '{source.name}' already exists in '{name}'."
            )

        project.sources.append(source)
        project.updated_at = util.utcnow()
        cls._save(project)
        return project

    @classmethod
    def remove_source(cls, name: str, source_name: str) -> models.Project:
        project = cls.get(name)
        if not any(s.name == source_name for s in project.sources):
            raise SourceNotFoundError(f"Source '{source_name}' not found in '{name}'.")
        project.sources = [s for s in project.sources if s.name != source_name]
        project.updated_at = util.utcnow()
        cls._save(project)
        return project

    @classmethod
    def _save(cls, project: models.Project) -> None:
        path = cls._path(project.name)
        with path.open("wb") as f:
            tomli_w.dump(project.model_dump(), f)
