from lakefront import util


def test_path_info_local_csv(tmp_path):
    # Test local path
    local_path = tmp_path / "data.csv"
    local_path.touch()
    info = util.fs.PathInfo(str(local_path), "testing")
    assert info.path == str(local_path)
    assert info.exists()
    assert info.is_local()
    assert not info.is_s3()
    assert info.is_file()
    assert not info.is_dir()
    assert info.get_type() == util.PathType.CSV
    assert info.is_csv()
    assert not info.is_parquet()
    assert not info.is_dataset()

    # Test S3 path
    s3_path = "s3://my-bucket/data.parquet"
    info = util.fs.PathInfo(s3_path, "testing")
    assert not info.is_local()
    assert info.is_s3()
    assert info.path == "my-bucket/data.parquet"


def test_path_info_local_parquet(tmp_path):
    # Test local path
    local_path = tmp_path / "data.parquet"
    local_path.touch()
    info = util.fs.PathInfo(str(local_path), "testing")
    assert info.exists()
    assert info.is_local()
    assert not info.is_s3()
    assert info.is_file()
    assert not info.is_dir()
    assert not info.is_csv()
    assert info.is_parquet()
    assert info.get_type() == util.PathType.PARQUET
    assert not info.is_dataset()


def test_path_info_local_dataset(tmp_path):
    # Create a directory with parquet files
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()
    (dataset_dir / "part1.parquet").touch()
    (dataset_dir / "part2.parquet").touch()

    info = util.fs.PathInfo(str(dataset_dir), "testing")
    assert info.exists()
    assert info.is_local()
    assert not info.is_s3()
    assert not info.is_file()
    assert info.is_dir()
    assert not info.is_csv()
    assert not info.is_parquet()
    assert info.get_type() == util.PathType.DATASET
    assert info.is_dataset()


def test_path_info_unknown(tmp_path):
    # Create a directory with non-parquet files
    unknown_dir = tmp_path / "unknown"
    unknown_dir.mkdir()
    (unknown_dir / "file.txt").touch()

    info = util.fs.PathInfo(str(unknown_dir), "testing")
    assert info.exists()
    assert info.is_local()
    assert not info.is_s3()
    assert not info.is_file()
    assert info.is_dir()
    assert not info.is_csv()
    assert not info.is_parquet()
    assert not info.is_dataset()
    assert info.get_type() == util.PathType.UNKNOWN
