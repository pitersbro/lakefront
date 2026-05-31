from lakefront import models


def test_data_source_model_accepts_different_schemes():
    ds1 = models.DataSource(name="Local File", uri="/path/to/file.csv")
    assert ds1.uri == "file:///path/to/file.csv"

    ds2 = models.DataSource(name="S3 Bucket", uri="s3://my-bucket/prefix/")
    assert ds2.uri == "s3://my-bucket/prefix/"

    ds3 = models.DataSource(name="HTTP Endpoint", uri="http://example.com/data")
    assert ds3.uri == "http://example.com/data"
