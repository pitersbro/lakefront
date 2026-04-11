def test_context_is_created(ctx):
    assert ctx.name == "test-project"
    assert ctx.profile == "default"
    assert len(ctx.sources) == 1


def test_context_source_can_be_queried_with_sql(ctx):
    result = ctx.query("SELECT * FROM 'file-1'").fetchdf()
    assert result.shape == (3, 2)
