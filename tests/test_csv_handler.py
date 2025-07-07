import pytest
import pandas as pd
from deta.csv_handler.csv_handler import CSVHandler


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
    handler.write_csv(df)

    loaded_df = pd.read_csv(file_path)
    assert loaded_df.equals(df)
