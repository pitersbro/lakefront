import sys
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).parent


def _resolve_env_file(default: str = "test.env") -> str:
    """Read the --env-file value straight from argv.

    The env file must be loaded at conftest import time, before any nested
    conftest imports ``lakefront.core`` and freezes ``LAKEFRONT_HOME`` from the
    environment. That happens during initial conftest loading, well before
    ``pytest_configure`` runs and option parsing is available — so we scan argv.
    """
    for i, arg in enumerate(sys.argv):
        if arg == "--env-file" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if arg.startswith("--env-file="):
            return arg.split("=", 1)[1]
    return default


# Redirect LAKEFRONT_HOME (via test.env) before core is imported anywhere.
load_dotenv(_resolve_env_file(), override=True)


def pytest_addoption(parser):
    parser.addoption("--env-file", default="test.env")


def pytest_configure(config):
    from lakefront import core, models

    conf = core.ProfileConfigurationService
    proj = core.ProjectConfigurationService
    try:
        import shutil

        shutil.rmtree(conf.home_dir())
        print("deleted", conf.home_dir().as_posix())
    except OSError:
        pass
    finally:
        core.initialize()

    conf.create_profile("testing")
    proj.create("test-project", profile="testing")

    proj.add_source(
        "test-project",
        models.DataSource(
            name="file_1",
            uri=(HERE / "tests/core/file1.parquet").as_posix(),
        ),
    )
    proj.add_source(
        "test-project",
        models.DataSource(
            name="file_2",
            uri=(HERE / "tests/core/file2.csv").as_posix(),
        ),
    )
    proj.add_source(
        "test-project",
        models.DataSource(
            name="dataset_1",
            uri=(HERE / "tests/core/dataset1").as_posix(),
        ),
    )
