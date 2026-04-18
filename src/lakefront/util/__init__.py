from datetime import datetime, timezone

from .fs import PathInfo, PathKind, PathType


def utcnow():
    return datetime.now(tz=timezone.utc)


__all__ = ["PathInfo", "PathKind", "PathType", "utcnow"]
