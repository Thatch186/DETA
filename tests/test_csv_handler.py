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


def test_add_a_count_column(tmp_path):
    # Setup
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

    # Act
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
