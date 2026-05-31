from __future__ import annotations

import re

from lakefront import models
from lakefront.log import logger

from . import context
from .analyzer import Analyzer
from .config import PROJECTS_DIR, ProjectConfigurationService, load_settings
from .engine import QueryEngineMixin, QueryResult
from .exceptions import LakefrontError, SourceExistsError, SourceNotFoundError
from .source import Source, resolve

_VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class Project(QueryEngineMixin):
    name: str

    def __init__(self, name):
        model = ProjectConfigurationService.get(name)
        self.name = model.name
        self.profile = model.profile

        self.settings = load_settings(profile=self.profile)
        self.set_context()
        self.sources = []
        # source_attach/source_detach both call reinitialize(), which reconstructs
        # ProjectContext from scratch, so _sources already reflects the updated list
        # and this guard stays correct after sources are added or removed at runtime.
        if any(src.uri.startswith("s3://") for src in model.sources):
            self.configure_s3()
        for src in model.sources:
            logger.debug(f'Loading source "{src.name}" from path: {src.uri}')
            source = resolve(src)
            if source.reachable():
                self.sources.append(source)
            else:
                logger.warning(
                    f'Source "{src.name}" skipped: path does not exist or is inaccessible.'
                )

        for source in self.sources:
            source.register(self.get_connection())

        self._ensure_log_file()

    @classmethod
    def load(cls, name: str):
        return cls(name)

    def analyzer(self) -> Analyzer:
        return Analyzer()

    def set_context(self):
        context.set_context(
            context.Context(
                self.profile,
                self.settings,
                self,
            )
        )

    def _ensure_log_file(self):
        self.home = PROJECTS_DIR / self.name
        self.home.mkdir(parents=True, exist_ok=True)
        self.log_file = self.home / "project.log"
        self.log_file.touch(exist_ok=True)

    def sources_by_type(self) -> dict[str, list[str]]:
        groups: dict[str, list[str]] = {}
        for src in self.sources:
            groups.setdefault(src.get_type(), []).append(src.name)
        sorted_groups = {
            k: sorted(v) for k, v in sorted(groups.items(), key=lambda x: x[0])
        }
        return sorted_groups

    def source_names(self) -> list[str]:
        return [src.name for src in self.sources]

    def source_get(self, name: str) -> Source:
        source = next((s for s in self.sources if s.name == name), None)
        if not source:
            raise SourceNotFoundError(
                f'Source with name "{name}" not found in project.'
            )
        return source

    def source_describe(self, name: str) -> QueryResult:
        src = self.source_get(name)
        return self.query(f"DESCRIBE {src.name}")

    def reinitialize(self) -> Project:
        """Reinitialize the project context, reloading all sources and settings."""
        obj = Project.load(self.name)
        self.__dict__.update(obj.__dict__)
        return self

    def source_attach(self, name: str, path: str) -> Project:
        """Attach a new source to the project and reinitialize the context."""
        if not _VALID_IDENTIFIER.match(name):
            raise LakefrontError(
                f'Invalid source name "{name}". '
                "Names must start with a letter or underscore and contain only "
                "letters, digits, and underscores."
            )
        new_source = models.DataSource(name=name, uri=path)
        if not resolve(new_source).reachable():
            raise LakefrontError(f'Path "{path}" does not exist or is inaccessible.')
        if any(s.name == name for s in self.sources):
            raise SourceExistsError(f'Source with name "{name}" already exists.')

        ProjectConfigurationService.add_source(self.name, new_source)
        return self.reinitialize()

    def source_detach(self, name: str) -> Project:
        """Detach a source from the project and reinitialize the context."""
        if not any(s.name == name for s in self.sources):
            raise SourceNotFoundError(f'Source with name "{name}" not found.')

        ProjectConfigurationService.remove_source(self.name, name)
        src = self.source_get(name)
        src.deregister(self.get_connection())
        return self.reinitialize()
