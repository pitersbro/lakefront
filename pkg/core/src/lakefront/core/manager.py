# from .models import ProjectDTO, ProjectRepository


class ProjectManager:
    pass


# class ProjectManager:
#     def __init__(self):
#         if not DB_PATH.exists():
#             raise RuntimeError("database not initialized. run: lakefront db init")
#         self.repo = ProjectRepository()
#
#     def create(self, name: str) -> ProjectDTO:
#         return self.repo.save(name)
#
#     def list(self) -> list[ProjectDTO]:
#         return self.repo.find_all()
#
#     def delete(self, name: str):
#         self.repo.delete(name)
#         if self.active() == name:
#             ACTIVE_PATH.unlink(missing_ok=True)
#
#     def switch(self, name: str):
#         if not self.repo.find_by_name(name):
#             raise ValueError(f"project '{name}' does not exist")
#         ACTIVE_PATH.write_text(name)
#
#     def active(self) -> str | None:
#         if ACTIVE_PATH.exists():
#             return ACTIVE_PATH.read_text().strip()
#         return None
