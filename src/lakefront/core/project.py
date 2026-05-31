from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from lakefront import models
from lakefront.log import logger

from . import fs
from .analyzer import Analyzer
from .config import PROJECTS_DIR, ProjectConfigurationService, Settings, load_settings
from .context import Context, set_context as _set_context
from .engine import QueryEngineMixin, QueryResult
from .exceptions import LakefrontError, SourceExistsError, SourceNotFoundError
from .source import Source, resolve

_VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass
class ProjectContext(QueryEngineMixin):
    name: str
    profile: str
    _sources: list[models.DataSource]
    sources: list[Source] = field(init=False)

    settings: Settings = field(init=False)
    log_file: Path = field(init=False)

    def __post_init__(self):
        self.settings = load_settings(profile=self.profile)
        self.set_context()
        self.sources = []
        # source_attach/source_detach both call reinitialize(), which reconstructs
        # ProjectContext from scratch, so _sources already reflects the updated list
        # and this guard stays correct after sources are added or removed at runtime.
        if any(src.uri.startswith("s3://") for src in self._sources):
            self.configure_s3()
        for src in self._sources:
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

    def analyzer(self) -> Analyzer:
        return Analyzer()

    def set_context(self):
        _set_context(Context(self.profile, self.settings, self))

    def _ensure_log_file(self):
        self.home = PROJECTS_DIR / self.name
        self.home.mkdir(parents=True, exist_ok=True)
        self.log_file = self.home / "project.log"
        self.log_file.touch(exist_ok=True)

    @classmethod
    def from_model(cls, project: models.Project) -> ProjectContext:
        return cls(
            name=project.name,
            profile=project.profile,
            _sources=project.sources,
        )

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

    def reinitialize(self) -> ProjectContext:
        """Reinitialize the project context, reloading all sources and settings."""
        project = ProjectConfigurationService.get(self.name)
        obj = ProjectContext.from_model(project)
        self.__dict__.update(obj.__dict__)
        return self

    def source_attach(self, name: str, path: str) -> ProjectContext:
        """Attach a new source to the project and reinitialize the context."""
        if not _VALID_IDENTIFIER.match(name):
            raise LakefrontError(
                f'Invalid source name "{name}". '
                "Names must start with a letter or underscore and contain only "
                "letters, digits, and underscores."
            )
        if not fs.PathInfo(path, self.profile).exists():
            raise LakefrontError(f'Path "{path}" does not exist or is inaccessible.')
        if any(s.name == name for s in self.sources):
            raise SourceExistsError(f'Source with name "{name}" already exists.')

        new_source = models.DataSource(name=name, uri=path)
        ProjectConfigurationService.add_source(self.name, new_source)
        return self.reinitialize()

    def source_detach(self, name: str) -> ProjectContext:
        """Detach a source from the project and reinitialize the context."""
        if not any(s.name == name for s in self.sources):
            raise SourceNotFoundError(f'Source with name "{name}" not found.')

        ProjectConfigurationService.remove_source(self.name, name)
        src = self.source_get(name)
        src.deregister(self.get_connection())
        return self.reinitialize()
