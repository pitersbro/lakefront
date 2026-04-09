from pathlib import Path

import tomli_w
import tomllib
from lakefront.core.config import PROJECTS_DIR
from lakefront.core.exceptions import (
    ProjectExistsError,
    ProjectNotFoundError,
    SourceExistsError,
    SourceNotFoundError,
)
from lakefront.core.models import DataSource, Project, utcnow


class ProjectService:
    @classmethod
    def _path(cls, name: str) -> Path:
        return PROJECTS_DIR / name / "project.toml"

    @classmethod
    def create(
        cls, name: str, description: str = "", profile: str = "default"
    ) -> Project:
        project_dir = PROJECTS_DIR / name
        if project_dir.exists():
            raise ProjectExistsError(f"Project '{name}' already exists.")

        project_dir.mkdir(parents=True)
        # TODO: Think about it
        # (project_dir / "results").mkdir()

        project = Project(name=name, description=description, profile=profile)
        cls._save(project)
        return project

    @classmethod
    def get(cls, name: str) -> Project:
        path = cls._path(name)
        if not path.exists():
            raise ProjectNotFoundError(f"Project '{name}' not found.")
        import tomllib

        with path.open("rb") as f:
            return Project(**tomllib.load(f))

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
    def add_source(cls, name: str, source: DataSource) -> Project:
        project = cls.get(name)
        if any(s.name == source.name for s in project.sources):
            raise SourceExistsError(
                f"Source '{source.name}' already exists in '{name}'."
            )
        project.sources.append(source)
        project.updated_at = utcnow()
        cls._save(project)
        return project

    @classmethod
    def remove_source(cls, name: str, source_name: str) -> Project:
        project = cls.get(name)
        if not any(s.name == source_name for s in project.sources):
            raise SourceNotFoundError(f"Source '{source_name}' not found in '{name}'.")
        project.sources = [s for s in project.sources if s.name != source_name]
        project.updated_at = utcnow()
        cls._save(project)
        return project

    @classmethod
    def _save(cls, project: Project) -> None:
        path = cls._path(project.name)
        with path.open("wb") as f:
            tomli_w.dump(project.model_dump(), f)

    @classmethod
    def _load(cls, name: str) -> Project: ...
