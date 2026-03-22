from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Source:
    id: int
    path: str
    alias: str | None
    added_at: datetime


@dataclass
class Project:
    id: int
    name: str
    created_at: datetime
    sources: list[Source] = field(default_factory=list)


class ProjectManager:
    def list_projects(self) -> list[Project]: ...
    def create(self, name: str) -> Project: ...
    def delete(self, name: str): ...
    def switch(self, name: str): ...
    def active(self) -> dict | None: ...
    def add_source(self, path: str, alias: str | None): ...
    def remove_source(self, source_id: int): ...
    def list_sources(self) -> list[dict]: ...
