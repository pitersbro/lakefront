from .config import ConfigurationService
from .manager import ProjectService


def get_version() -> str:
    import importlib.metadata as pkg

    return pkg.version("lakefront-core")


__all__ = [
    "ConfigurationService",
    "ProjectService",
    "get_version",
]
