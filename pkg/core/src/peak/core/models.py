from dataclasses import dataclass
from datetime import datetime

from .config import metadb


@dataclass
class ProjectDTO:
    id: int
    name: str
    created_at: datetime


class ProjectRepository:
    def find_by_name(self, name: str) -> ProjectDTO | None:
        with metadb() as db:
            row = db.execute(
                "SELECT id, name, created_at FROM projects WHERE name = ?", [name]
            ).fetchone()
        return ProjectDTO(id=row[0], name=row[1], created_at=row[2]) if row else None

    def find_all(self) -> list[ProjectDTO]:
        with metadb() as db:
            rows = db.execute(
                "SELECT id, name, created_at FROM projects ORDER BY created_at DESC"
            ).fetchall()
        return [ProjectDTO(id=r[0], name=r[1], created_at=r[2]) for r in rows]

    def save(self, name: str) -> ProjectDTO:
        with metadb() as db:
            row = db.execute(
                "INSERT INTO projects (name) VALUES (?) RETURNING id, name, created_at",
                [name],
            ).fetchone()
        return ProjectDTO(id=row[0], name=row[1], created_at=row[2])

    def delete(self, name: str):
        with metadb() as db:
            db.execute("DELETE FROM projects WHERE name = ?", [name])
