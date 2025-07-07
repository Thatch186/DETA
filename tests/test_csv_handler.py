from unittest.mock import MagicMock, mock_open, patch
import pytest
import pandas as pd
from deta.csv_handler.csv_handler import CSVHandler
import os


def test_read_csv_success(tmp_path):
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})
    df.to_csv(file_path, index=False)

    handler = CSVHandler(str(file_path))
    assert isinstance(handler.df, pd.DataFrame)
    assert handler.df.equals(df)


def test_read_csv_failure():
    with pytest.raises(ValueError, match="Error reading CSV file"):
        CSVHandler("nonexistent.csv")


def test_write_csv_success(tmp_path):
    file_path = tmp_path / "output.csv"
    df = pd.DataFrame({"C": [3, 4], "D": ["z", "w"]})
    df.to_csv(file_path, index=False)

    handler = CSVHandler(str(file_path))
    handler.write_csv()

    loaded_df = pd.read_csv(file_path)
    assert loaded_df.equals(df)


def test_add_a_count_column(tmp_path):
    test_data = pd.DataFrame(
        {
            "FinInstrmGnlAttrbts.FullNm": [
                "Alpha Asset",
                "Beta",
                "Gamma Capital",
                "",
                None,
            ]
        }
    )

    temp_file = tmp_path / "test.csv"
    test_data.to_csv(temp_file, index=False)

    handler = CSVHandler(str(temp_file))
    df = handler.add_a_count_column()

    expected_counts = [1, 1, 4, 0, 0]
    assert "a_count" in df.columns
    assert df["a_count"].tolist() == expected_counts


def test_add_contains_a_column(tmp_path):
    test_data = {
        "FinInstrmGnlAttrbts.FullNm": ["Alpha", "Beta", "Espsilon", "Uno"],
        "a_count": [1, 2, 0, 0],
    }
    df = pd.DataFrame(test_data)

    test_csv = tmp_path / "test.csv"
    df.to_csv(test_csv, index=False)

    handler = CSVHandler(str(test_csv))
    updated_df = handler.add_contains_a_column()

    assert "contains_a" in updated_df.columns
    assert updated_df["contains_a"].tolist() == ["YES", "YES", "NO", "NO"]


@pytest.fixture
def sample_csv_handler(tmp_path):
    file_path = tmp_path / "test.csv"
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    df.to_csv(file_path, index=False)
    handler = CSVHandler(str(file_path))
    handler.df = df  # Overwrite just in case
    return handler


def test_upload_local_success(sample_csv_handler, tmp_path):
    dest_path = tmp_path / "output" / "file.csv"

    sample_csv_handler.upload_file(
        destination_type="local", destination_path=str(dest_path)
    )

    assert os.path.exists(dest_path)
    df_loaded = pd.read_csv(dest_path)
    pd.testing.assert_frame_equal(df_loaded, sample_csv_handler.df)


@patch("fsspec.get_fs_token_paths")
def test_upload_s3_success(mock_fs_token, sample_csv_handler):
    mock_file = mock_open()
    mock_fs = MagicMock()
    mock_fs.open.return_value.__enter__.return_value = mock_file()
    mock_fs_token.return_value = (mock_fs, None, ["mock/path.csv"])

    sample_csv_handler.upload_file(
        destination_type="s3", destination_path="mock-bucket/test.csv"
    )

    mock_fs.open.assert_called_once_with("s3://mock-bucket/test.csv", "w")
    assert mock_file().write.called


@patch("fsspec.get_fs_token_paths")
def test_upload_blob_success(mock_fs_token, sample_csv_handler):
    mock_file = mock_open()
    mock_fs = MagicMock()
    mock_fs.open.return_value.__enter__.return_value = mock_file()
    mock_fs_token.return_value = (mock_fs, None, ["mock/path.csv"])

    sample_csv_handler.upload_file(
        destination_type="blob", destination_path="container/folder/file.csv"
    )

    mock_fs.open.assert_called_once_with("az://container/folder/file.csv", "w")
    assert mock_file().write.called


def test_upload_invalid_type_raises(sample_csv_handler):
    with pytest.raises(ValueError, match="Unsupported destination type"):
        sample_csv_handler.upload_file(
            destination_type="ftp", destination_path="invalid/path.csv"
        )
