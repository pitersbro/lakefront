import pytest

from lakefront import core


@pytest.fixture(scope="session")
def ctx():
    proj = core.get_project("test-project")
    yield proj
