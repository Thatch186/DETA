import pytest
from deta.xml_handler.xml_handler import XMLHandler
import zipfile
import os
import pandas as pd

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

CSV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<BizData xmlns="urn:iso:std:iso:20022:tech:xsd:head.003.001.01">
  <Pyld>
    <Document xmlns="urn:iso:std:iso:20022:tech:xsd:auth.036.001.02">
      <FinInstrmRptgRefDataDltaRpt>
        <FinInstrm>
          <ModfdRcrd>
            <FinInstrmGnlAttrbts>
              <Id>ABC123</Id>
              <FullNm>Alpha Corp</FullNm>
              <ClssfctnTp>EQTY</ClssfctnTp>
              <CmmdtyDerivInd>0</CmmdtyDerivInd>
              <NtnlCcy>USD</NtnlCcy>
            </FinInstrmGnlAttrbts>
            <Issr>Issuer123</Issr>
          </ModfdRcrd>
        </FinInstrm>
      </FinInstrmRptgRefDataDltaRpt>
    </Document>
  </Pyld>
</BizData>
"""


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


def create_test_zip(tmp_path, filename="test.zip", xml_inside=True, bad_zip=False):
    zip_path = tmp_path / filename

    if bad_zip:
        with open(zip_path, "wb") as f:
            f.write(b"not a zip file")
        return zip_path

    with zipfile.ZipFile(zip_path, "w") as zipf:
        if xml_inside:
            zipf.writestr("test_file.xml", "<root>data</root>")
        else:
            zipf.writestr("not_xml.txt", "irrelevant content")

    return zip_path


def test_extract_from_zip_success(tmp_path):
    zip_path = create_test_zip(tmp_path)
    extract_dir = tmp_path / "extracted"

    handler = XMLHandler("dummy.xml")
    result_path = handler.extract_from_zip(str(zip_path), str(extract_dir))

    assert result_path.endswith(".xml")
    assert os.path.exists(result_path)


def test_extract_from_zip_file_not_found(tmp_path):
    handler = XMLHandler("dummy.xml")
    missing_path = tmp_path / "missing.zip"

    with pytest.raises(FileNotFoundError):
        handler.extract_from_zip(str(missing_path), str(tmp_path))


def test_extract_from_zip_no_xml_inside(tmp_path):
    zip_path = create_test_zip(tmp_path, xml_inside=False)
    handler = XMLHandler("dummy.xml")

    with pytest.raises(ValueError, match="No XML files found"):
        handler.extract_from_zip(str(zip_path), str(tmp_path))


def test_extract_from_zip_bad_zip(tmp_path):
    zip_path = create_test_zip(tmp_path, bad_zip=True)
    handler = XMLHandler("dummy.xml")

    with pytest.raises(zipfile.BadZipFile):
        handler.extract_from_zip(str(zip_path), str(tmp_path))


def test_convert_to_csv(tmp_path):
    xml_path = tmp_path / "sample.xml"
    csv_path = tmp_path / "output.csv"

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(CSV_XML)

    handler = XMLHandler(str(xml_path))
    csv_path = handler.convert_to_csv(str(csv_path))
    df = pd.read_csv(csv_path)
    assert os.path.exists(csv_path)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1

    row = df.iloc[0]
    assert row["FinInstrmGnlAttrbts.Id"] == "ABC123"
    assert row["FinInstrmGnlAttrbts.FullNm"] == "Alpha Corp"
    assert row["FinInstrmGnlAttrbts.ClssfctnTp"] == "EQTY"
    assert row["FinInstrmGnlAttrbts.CmmdtyDerivInd"] == 0
    assert row["FinInstrmGnlAttrbts.NtnlCcy"] == "USD"
    assert row["Issr"] == "Issuer123"
