from deta.downloader.downloader import Downloader
from deta.xml_handler.xml_handler import XMLHandler
from deta.csv_handler.csv_handler import CSVHandler
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main() -> None:

    first_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"
    first_file_path = "data/first_url.xml"
    downloader = Downloader(retries=3, timeout=10)
    try:
        first_downloaded_path = downloader.download_from_url(first_url, first_file_path)
        logging.info(f"First file downloaded to: {first_downloaded_path}")
        handler = XMLHandler(first_file_path)
        xml_str = handler.read_xml()

        second_url = handler.parse_xml(xml_str, index=1)

        second_file_path = "data/second_url.zip"
        second_downloaded_path = downloader.download_from_url(
            second_url, second_file_path
        )

        extracted_xml_path = handler.extract_from_zip(
            second_downloaded_path, extract_to="data/extracted_xml"
        )
        second_handler = XMLHandler(extracted_xml_path)
        csv_path = second_handler.convert_to_csv(
            output_csv_path="data/extracted_xml/converted.csv"
        )

        csv_handler = CSVHandler(csv_path)
        csv_handler.add_a_count_column()
        csv_handler.add_contains_a_column()
        csv_handler.write_csv()

        csv_handler.upload_file(
            destination_type="local", destination_path="data/final/final.csv"
        )
        # csv_handler.upload_file(destination_type="s3", destination_path="mock-bucket/final.csv")
        # csv_handler.upload_file(destination_type="blob", destination_path="container/path/final.csv")
    except Exception as e:
        logging.error(f"Failed to download file: {e}")


if __name__ == "__main__":
    main()
