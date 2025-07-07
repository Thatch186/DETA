import os
import pandas as pd
import logging
import fsspec

logger = logging.getLogger(__name__)


class CSVHandler:
    def __init__(self, file_path: str):
        """
        Initializes the CSVHandler with a file path.
        Args:
            file_path: Path to the CSV file to be handled.
        """
        self.file_path = file_path
        self.df = self.read_csv(file_path)
        logging.debug(f"CSVHandler initialized with file_path={file_path}")

    def read_csv(self, csv_path) -> pd.DataFrame:
        """
        Reads a CSV file and returns a DataFrame.
        Args:
            csv_path: Path to the CSV file.
        """
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Successfully read CSV file: {csv_path}")
            return df
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")

    def write_csv(self) -> None:
        """
        Writes a DataFrame to a CSV file.
        Args:
            df: DataFrame to be written to the CSV file.
        """
        try:
            self.df.to_csv(self.file_path, index=False)
            logger.info(f"Successfully wrote DataFrame to CSV file: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Error writing to CSV file: {e}")

    def add_a_count_column(self) -> pd.DataFrame:
        """
        Adds a new column 'a_count' to the DataFrame, which counts the number of times
        the lowercase character 'a' appears in the 'FinInstrmGnlAttrbts.FullNm' column.
        """
        try:
            if "FinInstrmGnlAttrbts.FullNm" not in self.df.columns:
                raise ValueError(
                    "Column 'FinInstrmGnlAttrbts.FullNm' not found in the CSV."
                )

            self.df["a_count"] = self.df["FinInstrmGnlAttrbts.FullNm"].apply(
                lambda x: str(x).count("a") if pd.notna(x) else 0
            )
            return self.df

        except Exception as e:
            raise ValueError(f"Error adding 'a_count' column: {e}") from e

    def add_contains_a_column(self) -> pd.DataFrame:
        """
        Adds a 'contains_a' column to the DataFrame based on 'a_count'.
        If a_count > 0, contains_a is 'YES'; otherwise, 'NO'.
        """
        try:
            if "a_count" not in self.df.columns:
                raise ValueError(
                    "'a_count' column is missing. Run add_a_count_column first."
                )

            self.df["contains_a"] = self.df["a_count"].apply(
                lambda x: "YES" if x > 0 else "NO"
            )
            logger.info("Added 'contains_a' column based on 'a_count'.")
            return self.df
        except Exception as e:
            raise ValueError(f"Error adding 'contains_a' column: {e}") from e

    def upload_file(self, destination_type: str, destination_path: str) -> None:
        """
        Uploads the CSV to a specified destination: local, S3, or Azure blob.

        Args:
            destination_type: One of "local", "s3", or "blob"
            destination_path: File path or URI (e.g., "data/final.csv", "s3://bucket/folder/file.csv")

        Raises:
            ValueError: If upload fails or destination_type is invalid.
        """
        try:
            if destination_type == "local":
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                self.df.to_csv(destination_path, index=False)
                logger.info(f"CSV saved locally at: {destination_path}")

            elif destination_type in {"s3", "blob"}:
                protocol = "s3" if destination_type == "s3" else "az"
                url = f"{protocol}://{destination_path}"
                fs, _, paths = fsspec.get_fs_token_paths(url)

                with fs.open(url, "w") as f:
                    self.df.to_csv(f, index=False)

                logger.info(f"CSV uploaded to {destination_type.upper()} at: {url}")

            else:
                raise ValueError(f"Unsupported destination type: {destination_type}")

        except Exception as e:
            logger.error(
                f"Failed to upload CSV to {destination_type.upper()} at {destination_path}: {e}"
            )
            raise ValueError(f"Upload error: {e}") from e
