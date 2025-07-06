import pytest
from deta.xml_handler.xml_handler import XMLHandler

VALID_XML = """<?xml version="1.0" encoding="UTF-8"?>
<response>
  <result name="response" numFound="3" start="0">
    <doc>
      <str name="file_type">DLTINS</str>
      <str name="download_link">https://example.com/first.zip</str>
    </doc>
    <doc>
      <str name="file_type">DLTINS</str>
      <str name="download_link">https://example.com/second.zip</str>
    </doc>
    <doc>
      <str name="file_type">OTHER</str>
      <str name="download_link">https://example.com/other.zip</str>
    </doc>
  </result>
</response>
"""

MALFORMED_XML = "<response><doc><str></response>"  # Missing closing tag on <str>


def test_parse_xml_returns_correct_link():
    """
    Test that the XMLHandler correctly parses the XML and returns the download link
    """
    handler = XMLHandler("dummy.xml")
    link = handler.parse_xml(VALID_XML, index=1)
    assert link == "https://example.com/second.zip"


def test_parse_xml_raises_for_invalid_index():
    """
    Test that the XMLHandler raises ValueError for an index that is out of range."""
    handler = XMLHandler("dummy.xml")
    with pytest.raises(ValueError, match="index 3 is out of range"):
        handler.parse_xml(VALID_XML, index=3)


def test_parse_xml_raises_for_malformed_xml():
    """
    Test that the XMLHandler raises an exception for malformed XML."""
    handler = XMLHandler("dummy.xml")
    with pytest.raises(Exception):
        handler.parse_xml(MALFORMED_XML)


def test_read_xml_success(tmp_path):
    """
    Test that the XMLHandler reads a valid XML file correctly.
    """
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(VALID_XML, encoding="utf-8")

    handler = XMLHandler(str(xml_file))
    content = handler.read_xml()
    assert content == VALID_XML


def test_read_xml_file_not_found():
    """
    Test that the XMLHandler raises FileNotFoundError when the file does not exist.
    """
    handler = XMLHandler("nonexistent.xml")
    with pytest.raises(FileNotFoundError):
        handler.read_xml()
