import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from lakefront.core import (
    DataSource,
    ProfileConfigurationService,
    Project,
    ProjectContext,
)

HERE = Path(__file__).parent


@pytest.fixture(scope="session")
def mock_home_dir():
    temp_dir = tempfile.TemporaryDirectory()
    yield Path(temp_dir.name)
    temp_dir.cleanup()


@pytest.fixture(scope="session")
def mock_projects_dir(mock_home_dir):
    (mock_home_dir / "projects").mkdir(parents=True)
    (mock_home_dir / "config").mkdir(parents=True)
    (mock_home_dir / "state").touch()
    (mock_home_dir / "state").write_text("default")
    return mock_home_dir


@pytest.fixture(scope="session")
def mock_config(monkeypatch, mock_projects_dir):
    monkeypatch.setattr("lakefront.core.config.PROJECTS_DIR", mock_projects_dir)
    ProfileConfigurationService.create_profile("default")


@pytest.fixture(scope="function")
def mock_project_model():
    return Project(
        name="test-project",
        description="A test project",
        profile="default",
        sources=[
            DataSource(
                name="file-1", kind="local", path=(HERE / "file1.parquet").as_posix()
            ),
            # DataSource(name="s3-source", kind="s3", path="s3://my-bucket/data/"),
        ],
    )


@pytest.fixture
def mock_settings():
    s = MagicMock()  # no spec — allows arbitrary attribute access
    s.duckdb = MagicMock()
    s.duckdb.threads = 4
    s.duckdb.memory_limit = "2GB"
    s.s3 = MagicMock()
    s.s3.endpoint = ""
    return s


@pytest.fixture
def patched_load_settings(mock_settings):
    with patch("lakefront.core.config.load_settings", return_value=mock_settings) as m:
        yield m


@pytest.fixture(scope="function")
def ctx(
    monkeypatch, mock_project_model, mock_projects_dir, mock_home_dir, mock_settings
):
    monkeypatch.setattr("lakefront.core.config.PROJECTS_DIR", mock_projects_dir)
    monkeypatch.setattr("lakefront.core.config.LAKEFRONT_HOME", mock_home_dir)
    monkeypatch.setattr("lakefront.core.main.load_settings", lambda **_: mock_settings)
    return ProjectContext.from_model(mock_project_model)
