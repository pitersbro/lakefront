import pytest
from lakefront.core.exceptions import ProjectExistsError
from lakefront.core.manager import ProjectService


def test_list_projects_returns_names(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    monkeypatch.setattr("lakefront.core.manager.PROJECTS_DIR", projects_dir)

    for name in ["alpha", "beta"]:
        (projects_dir / name).mkdir(parents=True)
        (projects_dir / name / "project.toml").touch()

    assert ProjectService.list_projects() == ["alpha", "beta"]


def test_list_projects_skips_dirs_without_toml(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    monkeypatch.setattr("lakefront.core.manager.PROJECTS_DIR", projects_dir)

    (projects_dir / "ghost").mkdir(parents=True)  # no project.toml
    (projects_dir / "real").mkdir(parents=True)
    (projects_dir / "real" / "project.toml").touch()

    assert ProjectService.list_projects() == ["real"]


def test_create_makes_dir_structure(tmp_path, monkeypatch):
    monkeypatch.setattr("lakefront.core.manager.PROJECTS_DIR", tmp_path)

    project = ProjectService.create("my-project", description="test", profile="staging")

    assert (tmp_path / "my-project" / "project.toml").exists()
    # assert (tmp_path / "my-project" / "results").is_dir()
    assert project.name == "my-project"
    assert project.profile == "staging"


def test_create_raises_if_exists(tmp_path, monkeypatch):
    monkeypatch.setattr("lakefront.core.manager.PROJECTS_DIR", tmp_path)

    ProjectService.create("dupe")
    with pytest.raises(ProjectExistsError):
        ProjectService.create("dupe")
