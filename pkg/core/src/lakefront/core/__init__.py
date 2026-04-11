from .config import ProfileConfigurationService, ProjectConfigurationService, initialize
from .exceptions import (
    ProjectExistsError,
    ProjectNotFoundError,
    SourceExistsError,
    SourceNotFoundError,
)
from .models import DataSource, Project
from .viewer import ProjectViewer


def get_version() -> str:
    import importlib.metadata as pkg

    return pkg.version("lakefront-core")


__all__ = [
    "ProfileConfigurationService",
    "ProjectConfigurationService",
    "ProjectViewer",
    "get_version",
    "initialize",
    "ProjectExistsError",
    "ProjectNotFoundError",
    "SourceExistsError",
    "SourceNotFoundError",
    "DataSource",
    "Project",
]
