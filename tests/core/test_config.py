import operator

import pytest

from lakefront import core

svc = core.ProjectConfigurationService


def test_list_projects_returns_names(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    monkeypatch.setattr("lakefront.core.config.PROJECTS_DIR", projects_dir)

    for name in ["alpha", "beta"]:
        (projects_dir / name).mkdir(parents=True)
        (projects_dir / name / "project.toml").touch()

    assert svc.list_projects() == ["alpha", "beta"]


def test_list_projects_skips_dirs_without_toml(tmp_path, monkeypatch):
    projects_dir = tmp_path / "projects"
    monkeypatch.setattr("lakefront.core.config.PROJECTS_DIR", projects_dir)

    (projects_dir / "ghost").mkdir(parents=True)  # no project.toml
    (projects_dir / "real").mkdir(parents=True)
    (projects_dir / "real" / "project.toml").touch()

    assert svc.list_projects() == ["real"]


def test_create_makes_dir_structure(tmp_path, monkeypatch):
    monkeypatch.setattr("lakefront.core.config.PROJECTS_DIR", tmp_path)

    project = svc.create("my-project", description="test", profile="staging")

    assert (tmp_path / "my-project" / "project.toml").exists()
    # TODO: Think about it
    # assert (tmp_path / "my-project" / "results").is_dir()
    assert project.name == "my-project"
    assert project.profile == "staging"


def test_create_raises_if_exists(tmp_path, monkeypatch):
    monkeypatch.setattr("lakefront.core.config.PROJECTS_DIR", tmp_path)

    svc.create("dupe")
    with pytest.raises(core.ProjectExistsError):
        svc.create("dupe")


@pytest.mark.parametrize(
    "env_var,attr_path,value",
    [
        pytest.param("LAKEFRONT_CORE__THEME", "core.theme", "dracula", id="core.theme"),
        pytest.param(
            "LAKEFRONT_CORE__ANALYZER_ROW_LIMIT",
            "core.analyzer_row_limit",
            10,
            id="core.analyzer_row_limit",
        ),
        pytest.param(
            "LAKEFRONT_S3__ENDPOINT",
            "s3.endpoint",
            "https://s3.example.com",
            id="s3.endpoint",
        ),
    ],
)
def test_settings_toml_properties_overriden_by_corresponsing_env_vars(
    env_var, attr_path, value, monkeypatch
):
    monkeypatch.setenv(env_var, value)

    settings = core.load_settings("testing")
    assert operator.attrgetter(attr_path)(settings) == value


def test_settings_do_pick_up_unsupported_env_var(monkeypatch):
    monkeypatch.setenv("LAKEFRONT_CUSTOM__VALUE", "custom123")

    settings = core.load_settings("testing")
    with pytest.raises(AttributeError):
        settings.custom.value == "custom123"  # type: ignore
