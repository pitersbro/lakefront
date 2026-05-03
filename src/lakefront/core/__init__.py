from .config import (
    ProfileConfigurationService,
    ProjectConfigurationService,
    initialize,
    lakefront_settings,
    load_settings,
)
from .demo import ensure_demo_project
from .exceptions import (
    LlmError,
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
    "ensure_demo_project",
    "get_project",
    "lakefront_settings",
    "load_settings",
    "list_projects",
    "LlmError",
    "get_version",
    "initialize",
    "ProjectExistsError",
    "ProjectNotFoundError",
    "SourceExistsError",
    "SourceNotFoundError",
    "SourceTypeInvalidError",
]
