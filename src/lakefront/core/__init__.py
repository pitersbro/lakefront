from .config import (
    ProfileConfigurationService,
    ProjectConfigurationService,
    initialize,
    load_settings,
)
from .exceptions import (
    ProjectExistsError,
    ProjectNotFoundError,
    SourceExistsError,
    SourceNotFoundError,
    SourceTypeInvalidError,
)
from .main import ProjectContext


def get_version() -> str:
    import importlib.metadata as pkg

    return pkg.version("lakefront")


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
    "load_settings",
    "list_projects",
    "get_version",
    "initialize",
    "ProjectExistsError",
    "ProjectNotFoundError",
    "SourceExistsError",
    "SourceNotFoundError",
    "SourceTypeInvalidError",
]
