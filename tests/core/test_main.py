import pytest

from lakefront import core


@pytest.fixture(scope="module")
def ctx():
    proj = core.get_project("test-project")
    yield proj


def test_context_is_created(ctx):
    assert ctx.name == "test-project"
    assert ctx.profile == "testing"
    assert len(ctx.sources) == 3


def test_context_all_attached_source_types_can_be_queried_with_sql(ctx):
    for source in ctx.sources:
        result = ctx.query(f"SELECT * FROM '{source.source.name}'").fetchdf()
        assert result.shape == (3, 4)


def test_context_all_attached_source_types_can_be_described(ctx):
    for source in ctx.sources:
        description = ctx.source_describe(source.name).df()
        assert "column_type" in description.columns
        assert "column_name" in description.columns


def test_context_sources_can_be_grouped_by_type(ctx):
    groups = ctx.sources_by_type()
    assert "csv" in groups
    assert "dataset" in groups
    assert len(groups["csv"]) == 1
    assert len(groups["dataset"]) == 1
    assert len(groups["parquet"]) == 1


def test_context_source_not_found_ignored():
    model = core.Project(
        name="bad-project",
        profile="default",
        sources=[
            core.DataSource(name="weird_source", kind="local", path="/path/to/data")
        ],
    )
    ctx = core.ProjectContext.from_model(model)
    assert len(ctx.sources) == 0


def test_context_source_invalid_type_raises_validation_error():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        core.Project(
            name="bad-project",
            profile="default",
            sources=[
                core.DataSource(
                    name="bad_source", kind="unknown_kind", path="/path/to/data"
                )
            ],
        )


def test_context_source_attach_invalid_ignored(ctx):
    src = "nonexisting.csv"
    ctx.source_attach("myfile", kind="local", path=src)
    assert len(ctx.sources) == 3


def test_context_attach_detach_source_cycle(tmp_path, ctx):
    src = tmp_path / "file1.csv"
    src.touch()
    ctx.source_attach("attached1", path=src.as_posix(), kind="local")
    assert len(ctx.sources) == 4
    assert ctx.query("select * from attached1").df().shape == (0, 1)

    ctx.source_detach("attached1")
    assert len(ctx.sources) == 3
    with pytest.raises(Exception, match="Catalog Error"):
        assert ctx.query("select * from attached1")
