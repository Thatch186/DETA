import pandas as pd
import logging

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

    def write_csv(self, df: pd.DataFrame) -> None:
        """
        Writes a DataFrame to a CSV file.
        Args:
            df: DataFrame to be written to the CSV file.
        """
        try:
            df.to_csv(self.file_path, index=False)
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
