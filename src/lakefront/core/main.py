from __future__ import annotations

from dataclasses import dataclass

from lakefront import models
from lakefront.log import logger

from .analyzer import Analyzer
from .base import ContextBase, QueryResult, Source
from .config import PROJECTS_DIR, ProjectConfigurationService, load_settings
from .exceptions import SourceNotFoundError
from .query import QueryEngineMixin


@dataclass
class ProjectContext(QueryEngineMixin, ContextBase):
    def __post_init__(self):
        self.settings = load_settings(profile=self.profile)
        self.sources = []
        # source_attach/source_detach both call reinitialize(), which reconstructs
        # ProjectContext from scratch, so _sources already reflects the updated list
        # and this guard stays correct after sources are added or removed at runtime.
        if any(src.path.startswith("s3://") for src in self._sources):
            self.configure_s3()
        for src in self._sources:
            logger.debug(f'Loading source "{src.name}" from path: {src.path}')
            source = Source(self, src)
            if source.info.exists():
                self.sources.append(source)
            else:
                logger.warning(
                    f'Source "{src.name}" skipped: path does not exist or is inaccessible.'
                )

        for source in self.sources:
            self.register_source(source)

        self._ensure_log_file()

    def analyzer(self) -> Analyzer:
        return Analyzer(self)

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
            groups.setdefault(src.info.get_type().value, []).append(src.name)
        sorted_groups = {
            k: sorted(v) for k, v in sorted(groups.items(), key=lambda x: x[0])
        }
        return sorted_groups

    def source_names(self) -> list[str]:
        return [src.source.name for src in self.sources]

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

    def source_attach(self, name: str, path: str, kind: str) -> ProjectContext:
        """Attach a new source to the project and reinitialize the context."""
        if any(s.name == name for s in self.sources):
            raise ValueError(f'Source with name "{name}" already exists.')

        new_source = models.DataSource(name=name, path=path)
        ProjectConfigurationService.add_source(self.name, new_source)
        return self.reinitialize()

    def source_detach(self, name: str) -> ProjectContext:
        """Detach a source from the project and reinitialize the context."""
        if not any(s.name == name for s in self.sources):
            raise SourceNotFoundError(f'Source with name "{name}" not found.')

        ProjectConfigurationService.remove_source(self.name, name)
        self.deregister_source(name)
        return self.reinitialize()
