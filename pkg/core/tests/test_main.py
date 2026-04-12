import pytest
from lakefront.core import DataSource, Project, ProjectContext, SourceTypeInvalidError


def test_context_is_created(ctx):
    assert ctx.name == "test-project"
    assert ctx.profile == "default"
    assert len(ctx.sources) == 3


def test_context_all_attached_source_types_can_be_queried_with_sql(ctx):
    for source in ctx.sources:
        result = ctx.query(f"SELECT * FROM '{source.source.name}'").fetchdf()
        assert result.shape == (3, 4)


def test_context_invalid_source_type_error(patch_env):
    project = Project(
        name="bad-project",
        profile="default",
        sources=[DataSource(name="weird_source", kind="local", path="/path/to/data")],
    )
    with pytest.raises(
        SourceTypeInvalidError, match="Unsupported source type for path"
    ):
        ProjectContext.from_model(project)
