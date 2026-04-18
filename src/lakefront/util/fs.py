from enum import Enum
from functools import lru_cache

import pyarrow.fs as fs


class PathType(Enum):
    FILE = "FILE"
    DATASET = "DATASET"
    CSV = "CSV"
    PARQUET = "PARQUET"
    UNKNOWN = "UNKNOWN"


class PathKind(Enum):
    LOCAL = "LOCAL"
    S3 = "S3"


S3_PREFIX = "s3://"


def resolve_filesystem(path: str, profile: str) -> fs.FileSystem:
    """
    Resolves the appropriate PyArrow filesystem for the given path.
    Supports local paths and S3 paths (starting with s3://).
    """

    from lakefront.core import load_settings

    settings = load_settings(profile)
    if path.startswith("s3://"):
        kwargs = {
            "access_key": settings.s3.access_key,
            "secret_key": settings.s3.secret_key,
            "endpoint_override": settings.s3.endpoint_host,
            "region": settings.s3.region,
            "allow_bucket_creation": True,
            "allow_bucket_deletion": False,
            "retry_strategy": fs.AwsStandardS3RetryStrategy(max_attempts=10),
            "scheme": settings.s3.url_scheme,
        }
        return fs.S3FileSystem(**kwargs)
    else:
        return fs.LocalFileSystem()


class PathInfo:
    """Encapsulates information about a file path,
    including its type and filesystem."""

    def __init__(self, path: str, profile: str):
        self.path = path
        self.fs = resolve_filesystem(path, profile)
        self._is_s3 = False
        if self.path.startswith(S3_PREFIX):
            self._is_s3 = True
            # For S3 paths, we want to remove the "s3://"
            # prefix for filesystem operations
            self.path = path[len(S3_PREFIX) :]

    @lru_cache(maxsize=128)
    def exists(self) -> bool:
        return self.fs.get_file_info(self.path).type != fs.FileType.NotFound

    def is_local(self) -> bool:
        return self.path.startswith(S3_PREFIX) == False

    def is_s3(self) -> bool:
        return self._is_s3

    def kind(self) -> PathKind:
        if self.path.startswith(S3_PREFIX):
            return PathKind.S3
        else:
            return PathKind.LOCAL

    @lru_cache(maxsize=128)
    def is_file(self) -> bool:
        return self.fs.get_file_info(self.path).type == fs.FileType.File

    @lru_cache(maxsize=128)
    def is_dir(self) -> bool:
        return self.fs.get_file_info(self.path).type == fs.FileType.Directory

    def is_dataset(self) -> bool:
        if self.is_dir():
            for file_info in self.fs.get_file_info(
                fs.FileSelector(self.path, recursive=True)
            ):
                if file_info.is_file and file_info.path.endswith(".parquet"):
                    return True
        return False

    def is_csv(self) -> bool:
        if self.is_file() and self.path.endswith(".csv"):
            return True
        return False

    def is_parquet(self) -> bool:
        if self.is_file() and self.path.endswith(".parquet"):
            return True
        return False

    def get_type(self) -> PathType:
        if self.is_parquet():
            return PathType.PARQUET
        elif self.is_csv():
            return PathType.CSV
        elif self.is_dataset():
            return PathType.DATASET
        else:
            return PathType.UNKNOWN

    def __str__(self):
        return self.path

    def __repr__(self):
        return f"PathInfo(path='{self.path}')"
