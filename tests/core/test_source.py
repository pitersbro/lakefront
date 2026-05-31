import pytest

from lakefront import core, models
from lakefront.core.source import LocalFile, resolve


@pytest.fixture(scope="session")
def ctx():
    proj = core.get_project("test-project")
    yield proj


@pytest.fixture(scope="function")
def temp_csv(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.touch()
    return str(csv_path)


def test_local_file(ctx):
    source = resolve(ctx._sources[0])
    assert isinstance(source, LocalFile)
    assert source.name == "file_1"
    assert source.reachable() == True
    assert source.get_type() == "PARQUET"


def test_local_file_with_scheme(temp_csv):
    source = resolve(models.DataSource(name="file_2", uri=f"file://{temp_csv}"))
    assert isinstance(source, LocalFile)
    assert source.name == "file_2"
    assert source.reachable() == True
    assert source.get_type() == "CSV"


def test_local_file_without_scheme(temp_csv):
    source = resolve(models.DataSource(name="file_3", uri=temp_csv))
    assert isinstance(source, LocalFile)
    assert source.name == "file_3"
    assert source.reachable() == True
    assert source.get_type() == "CSV"


def test_local_file_not_reachable():
    source = resolve(models.DataSource(name="file_4", uri="/path/does/not/exist.csv"))
    assert isinstance(source, LocalFile)
    assert source.name == "file_4"
    assert source.reachable() == False
    assert source.get_type() == "UNKNOWN"
