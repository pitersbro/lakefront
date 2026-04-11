def test_context(ctx):
    assert ctx.name == "test-project"
    assert ctx.profile == "default"
    assert len(ctx.sources) == 1


def test_context_query(ctx):
    result = ctx.query("SELECT * FROM 'file-1'").fetchdf()
    assert result.shape == (3, 2)
