from dataclasses import dataclass
from typing import Any

from .config import Settings


@dataclass
class Context:
    profile: str
    settings: Settings
    project: Any


current_context: Context | None = None


def get_context() -> Context:
    """Get the current project context. Raises an error if no context is set."""
    if current_context is None:
        raise LookupError("No project context set. Call set_context() first.")
    return current_context


def set_context(context: Context):
    """Set the current project context by assigning it to the context variable."""
    global current_context
    current_context = context
