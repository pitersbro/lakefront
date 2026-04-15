# conftest.py
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).parent


def pytest_addoption(parser):
    parser.addoption("--env-file", default="test.env")


def pytest_configure(config):
    env_file = config.getoption("--env-file", default="test.env")
    load_dotenv(env_file, override=True)

    from lakefront import core

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
        core.models.DataSource(
            name="file_1",
            kind="local",
            path=(HERE / "tests/core/file1.parquet").as_posix(),
        ),
    )
    proj.add_source(
        "test-project",
        core.models.DataSource(
            name="file_2",
            kind="local",
            path=(HERE / "tests/core/file2.csv").as_posix(),
        ),
    )
    proj.add_source(
        "test-project",
        core.models.DataSource(
            name="dataset_1",
            kind="local",
            path=(HERE / "tests/core/dataset1").as_posix(),
        ),
    )
