from .explorer import Explorer
from .manager import ProjectManager


def hello() -> str:
    return "hello from lop-core"


__all__ = ["ProjectManager", "Explorer"]
