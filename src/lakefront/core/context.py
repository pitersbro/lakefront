# context.py
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

from .config import Settings


@dataclass
class Context:
    profile: str
    settings: Settings
    project: Any


current_context: ContextVar[Context] = ContextVar("current_context")


def get_context() -> Context:
    """Get the current project context from the context variable."""
    return current_context.get()


def set_context(context: Context):
    """Set the current project context in the context variable."""
    current_context.set(context)
