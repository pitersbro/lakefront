class LakefrontError(Exception):
    """Base class for all Lakefront exceptions."""


class ProjectNotFoundError(LakefrontError):
    """Raised when a project is not found."""

    def __init__(self, name: str):
        super().__init__(f"Project '{name}' not found.")
        self.name = name
