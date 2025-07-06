import pytest
from unittest.mock import patch, MagicMock
from deta.downloader.downloader import Downloader
import os
from requests.exceptions import RequestException


def test_download_success(tmp_path):
    """
    Test successful download of a file from a URL.
    """
    url = "https://example.com/file.xml"
    file_path = tmp_path / "downloaded.xml"

    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.content = b"<xml>hello</xml>"
    fake_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=fake_response) as mock_get:
        downloader = Downloader()
        result = downloader.download_from_url(url, str(file_path))

        mock_get.assert_called_once_with(url, timeout=10)
        assert os.path.exists(result)
        with open(result, "rb") as f:
            assert f.read() == b"<xml>hello</xml>"


def test_download_retries_on_request_exception():
    """
    Test that the downloader retries on a RequestException.
    """
    url = "https://example.com/fail.xml"

    with patch(
        "requests.get", side_effect=RequestException("Network error")
    ) as mock_get:
        downloader = Downloader(retries=3)
        with pytest.raises(RequestException, match="Network error"):
            downloader.download_from_url(url, "irrelevant/path.xml")
        assert mock_get.call_count == 3


def test_download_fails_on_unexpected_exception():
    """
    Test that the downloader fails hard on an unexpected exception.
    """
    url = "https://example.com/fail-hard.xml"

    with patch(
        "requests.get", side_effect=ValueError("Something unexpected")
    ) as mock_get:
        downloader = Downloader(retries=3)
        with pytest.raises(ValueError, match="Something unexpected"):
            downloader.download_from_url(url, "irrelevant/path.xml")
        # Should not retry — only 1 attempt
        assert mock_get.call_count == 1
