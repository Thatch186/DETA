from deta.downloader.downloader import Downloader
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main() -> None:

    first_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"
    first_file_path = "data/first_url.xml"
    downloader = Downloader(retries=3, timeout=10)
    try:
        downloaded_path = downloader.download_from_url(first_url, first_file_path)
        logging.info(f"File downloaded successfully to {downloaded_path}")
    except Exception as e:
        logging.error(f"Failed to download file: {e}")


if __name__ == "__main__":
    main()
