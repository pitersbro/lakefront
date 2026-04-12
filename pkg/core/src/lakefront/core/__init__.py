from .config import ProfileConfigurationService, ProjectConfigurationService, initialize
from .exceptions import (
    ProjectExistsError,
    ProjectNotFoundError,
    SourceExistsError,
    SourceNotFoundError,
    SourceTypeInvalidError,
)
from .main import ProjectContext
from .models import DataSource, Project


def get_version() -> str:
    import importlib.metadata as pkg

    return pkg.version("lakefront-core")


def get_project(name: str) -> ProjectContext:
    project = ProjectConfigurationService.get(name)
    return ProjectContext.from_model(project)


def list_projects() -> list[str]:
    return ProjectConfigurationService.list_projects()


__all__ = [
    "ProfileConfigurationService",
    "ProjectConfigurationService",
    "ProjectContext",
    "get_project",
    "list_projects",
    "get_version",
    "initialize",
    "ProjectExistsError",
    "ProjectNotFoundError",
    "SourceExistsError",
    "SourceNotFoundError",
    "SourceTypeInvalidError",
    "DataSource",
    "Project",
]
