from .config import ConfigurationService
from .manager import ProjectManager


def get_version() -> str:
    import importlib.metadata as pkg

    return pkg.version("lakefront-core")


__all__ = [
    "ConfigurationService",
    "ProjectManager",
    "get_version",
]
