from .bootstrap import bootstrap, teardown
from .explorer import Explorer
from .manager import ProjectManager


def get_version() -> str:
    import importlib.metadata as pkg

    return pkg.version("peak-core")


__all__ = ["ProjectManager", "Explorer", "bootstrap", "teardown", "get_version"]
