from dataclasses import dataclass
from datetime import datetime

from .config import make_project_path, metadb


@dataclass
class ProjectDTO:
    id: int
    name: str
    path: str
    created_at: datetime

    @classmethod
    def from_record(cls, record: tuple) -> "ProjectDTO":
        return cls(id=record[0], name=record[1], path=record[2], created_at=record[3])


class ProjectConfig:
    def __init__(self, project_id: int):
        self.project_id = project_id


class ProjectRepository:
    def find_by_name(self, name: str) -> ProjectDTO | None:
        with metadb() as db:
            row = db.execute(
                "SELECT id, name, path, created_at FROM projects WHERE name = ?", [name]
            ).fetchone()
        return ProjectDTO.from_record(row) if row else None

    def find_all(self) -> list[ProjectDTO]:
        with metadb() as db:
            rows = db.execute(
                "SELECT id, name, path, created_at FROM projects ORDER BY created_at DESC"
            ).fetchall()
        return [ProjectDTO.from_record(row) for row in rows]

    def save(self, name: str) -> ProjectDTO:
        path = make_project_path(name)
        with metadb() as db:
            row = db.execute(
                "INSERT INTO projects (name, path) VALUES (?, ?) RETURNING id, name, path, created_at",
                [name, str(path)],
            ).fetchone()
        return ProjectDTO.from_record(row)

    def delete(self, name: str):
        with metadb() as db:
            db.execute("DELETE FROM projects WHERE name = ?", [name])
