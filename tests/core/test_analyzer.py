import pandas as pd


def test_analyze_sql(ctx):
    sql = "SELECT name, age FROM file_2"
    profile = ctx.analyzer().analyze_sql(sql)
    assert profile["source"] == "query_result"
    assert profile["rows"] == 3
    assert profile["columns"] == 2
    assert profile["schema"]["name"] == {"type": "str", "null_pct": 0.0}
    assert profile["schema"]["age"] == {"type": "int64", "null_pct": 0.0}
    assert profile["stats"]["name"] == {
        "unique": 3,
        "top_values": {"Alice": 1, "Bob": 1, "Charlie": 1},
    }


def test_analyze_source(ctx):
    profile = ctx.analyzer().analyze_source("file_1")
    assert profile["source"] == "file_1"
    assert profile["rows"] == 3
    assert profile["columns"] == 4
    assert profile["schema"]["id"] == {"type": "int64", "null_pct": 0.0}


def test_analyze_pandas(ctx):
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [10.0, 20.5, 30.2],
            "category": ["A", "B", "A"],
        }
    )
    profile = ctx.analyzer().analyze_pandas(df, name="test_df")
    assert profile["source"] == "test_df"
    assert profile["rows"] == 3
    assert profile["columns"] == 3
    assert profile["schema"]["id"] == {"type": "int64", "null_pct": 0.0}
    assert profile["schema"]["value"] == {"type": "float64", "null_pct": 0.0}
    assert profile["schema"]["category"] == {"type": "str", "null_pct": 0.0}
    assert profile["stats"]["id"] == {
        "min": 1,
        "max": 3,
        "mean": 2.0,
        "median": 2.0,
        "std": 1.0,
        "p25": 1.5,
        "p75": 2.5,
    }
    assert profile["stats"]["value"] == {
        "min": 10.0,
        "max": 30.2,
        "mean": 20.2333,
        "median": 20.5,
        "std": 10.1026,
        "p25": 15.25,
        "p75": 25.35,
    }
    assert profile["stats"]["category"] == {"unique": 2, "top_values": {"A": 2, "B": 1}}
