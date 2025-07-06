from deta.downloader.downloader import Downloader
from deta.xml_handler.xml_handler import XMLHandler
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
        logging.info(f"File downloaded successfully to {first_downloaded_path}")

        handler = XMLHandler(first_file_path)
        xml_str = handler.read_xml()
        logging.info("XML file read successfully.")

        second_url = handler.parse_xml(xml_str, index=1)
        logging.info(f"Second URL extracted: {second_url}")

        second_file_path = "data/second_url.zip"
        second_downloaded_path = downloader.download_from_url(
            second_url, second_file_path
        )
        logging.info(f"Second file downloaded successfully to {second_downloaded_path}")

    except Exception as e:
        logging.error(f"Failed to download file: {e}")


if __name__ == "__main__":
    main()
