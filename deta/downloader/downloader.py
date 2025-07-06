import requests
import logging
import os
import time

logger = logging.getLogger(__name__)
SLEEP_TIME = 2


class Downloader:
    """
    Handles Downloads and Storing data from HTTP URL's, with all needed management.
    """

    def __init__(self, retries: int = 3, timeout: int = 10):
        """
        Initiates an instance of the Downloader class.

        Args:
            retries: number of retries the download request should be done in case of failure
            timeout: number of seconds to wait before aborting the request and start a new one
        """
        self.retries = retries
        self.timeout = timeout
        logger.debug(
            f"Downloader initialized with retries={retries} and timeout={timeout}"
        )

    def download_from_url(self, url: str, path: str):
        """
        Downloads a file from the given URL and stores it at the specified path.
        Args:
            url: url to download from
            path: path to store the downloaded file
        """
        for attempt in range(1, self.retries + 1):
            try:
                logger.info(f"Attempt {attempt}: Downloading from {url}")
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Successfully downloaded and saved file to: {path}")
                return path
            except requests.RequestException as e:
                logger.warning(f"Download attempt {attempt} failed: {e}")
                if attempt < self.retries:
                    time.sleep(SLEEP_TIME)
                else:
                    logger.error(
                        f"All {self.retries} download attempts failed for {url}"
                    )
                    raise
