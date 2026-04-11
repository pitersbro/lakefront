from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pyarrow as pa
import pyarrow.dataset as ds

from .config import load_settings
from .models import DataSource, Project


@dataclass
class Profiler:
    source: Source

    def rowcount(self) -> int:
        return self.source.data.count_rows()

    def schema(self) -> pa.Schema:
        return self.source.data.schema


@dataclass
class Source:
    project: ProjectViewer
    source: DataSource
    data: ds.Dataset = field(init=False)
    path: Path = field(init=False)

    def __post_init__(self):
        self.path = Path(self.source.path)
        self.data = ds.dataset(self.path.as_posix())

    def profiler(self):
        return Profiler(self)

    def __str__(self):
        return f"{self.source.name} ({self.source.kind})"


class ProjectViewer:
    def __init__(self, name: str, profile: str, sources: list[DataSource]):
        self.name = name
        self.profile = profile
        self.settings = load_settings(profile=self.profile)
        self.sources = [Source(self, src) for src in sources]

    @classmethod
    def from_model(cls, project: Project) -> ProjectViewer:
        return cls(
            name=project.name,
            profile=project.profile,
            sources=project.sources,
        )
