import logging
import xml.etree.ElementTree as ET
import zipfile
import os
import pandas as pd

logger = logging.getLogger(__name__)


class XMLHandler:
    """
    Handles XML file parsing and needed management.
    """

    def __init__(self, file_path: str):
        """
        Initiates an instance of the XMLHandler class.

        Args:
            file_path: path to the XML file to be handled
        """
        self.file_path = file_path
        logger.debug(f"XMLHandler initialized with file_path={file_path}")

    def read_xml(self) -> str:
        """
        Reads and returns the content of the XML file.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                content = file.read()
            logger.info(f"Successfully read XML file: {self.file_path}")
            return content
        except FileNotFoundError:
            logger.error(f"XML file not found: {self.file_path}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected error reading XML file: {e}", exc_info=True)
            raise

    def parse_xml(self, xml_content: str, index: int = 1) -> str:
        """
        Parses the XML and returns the nth DLTINS download link.

        Args:
            xml_content: Raw XML content as a string.
            index: Zero-based index of the DLTINS file to return.

        Returns:
            Download link as a string.

        Raises:
            ValueError: If the index is out of range.
        """
        try:
            root = ET.fromstring(xml_content)
            links = []

            for doc in root.findall(".//doc"):
                file_type = None
                download_link = None

                for elem in doc.findall("str"):
                    name = elem.attrib.get("name")
                    if name == "file_type":
                        file_type = elem.text
                    elif name == "download_link":
                        download_link = elem.text

                if file_type == "DLTINS" and download_link:
                    links.append(download_link)

            if len(links) <= index:
                raise ValueError(
                    f"Only {len(links)} DLTINS links found, index {index} is out of range."
                )

            logger.info(f"Found DLTINS download link: {links[index]}")
            return links[index]

        except ET.ParseError as e:
            logger.error(f"Failed to parse XML: {e}")
            raise
        except Exception as e:
            logger.critical(f"Unexpected XML parsing error: {e}", exc_info=True)
            raise

    def extract_from_zip(self, zip_path: str, extract_to: str) -> str:
        """
        Extracts the first XML file found inside the given ZIP archive.

        Args:
            zip_path: Path to the ZIP file.
            extract_to: Directory to extract the contents to.

        Returns:
            Path to the extracted XML file.

        Raises:
            FileNotFoundError: If zip_path does not exist.
            ValueError: If no XML file is found inside the ZIP.
        """
        try:
            if not os.path.exists(zip_path):
                raise FileNotFoundError(f"ZIP file not found: {zip_path}")

            os.makedirs(extract_to, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                xml_files = [f for f in zip_ref.namelist() if f.endswith(".xml")]
                if not xml_files:
                    raise ValueError("No XML files found inside the ZIP archive.")

                xml_file_name = xml_files[0]
                zip_ref.extract(xml_file_name, path=extract_to)
                extracted_path = os.path.join(extract_to, xml_file_name)

                logger.info(f"Extracted XML file: {extracted_path}")
                return extracted_path

        except FileNotFoundError as e:
            logger.error(f"ZIP file not found: {e}")
            raise

        except zipfile.BadZipFile as e:
            logger.error(f"Bad ZIP file: {e}")
            raise

        except Exception as e:
            logger.critical(
                f"Unexpected error while extracting ZIP file: {e}", exc_info=True
            )
            raise

    def convert_to_csv(self, output_csv_path: str) -> str:
        """
        Converts a large XML file to CSV by streaming FinInstrm nodes.

        Args:
            output_csv_path: Path to output CSV file.

        Returns:
            pandas DataFrame containing the parsed data.
        """
        ns = {
            "h": "urn:iso:std:iso:20022:tech:xsd:head.003.001.01",
            "a": "urn:iso:std:iso:20022:tech:xsd:auth.036.001.02",
        }

        records = []
        try:
            context = ET.iterparse(self.file_path, events=("end",))
            for event, elem in context:
                if elem.tag.endswith("FinInstrm"):
                    try:
                        gnl = elem.find(".//a:FinInstrmGnlAttrbts", ns)
                        issr = elem.findtext(".//a:Issr", default="", namespaces=ns)

                        row = {
                            "FinInstrmGnlAttrbts.Id": (
                                gnl.findtext("a:Id", default="", namespaces=ns)
                                if gnl is not None
                                else ""
                            ),
                            "FinInstrmGnlAttrbts.FullNm": (
                                gnl.findtext("a:FullNm", default="", namespaces=ns)
                                if gnl is not None
                                else ""
                            ),
                            "FinInstrmGnlAttrbts.ClssfctnTp": (
                                gnl.findtext("a:ClssfctnTp", default="", namespaces=ns)
                                if gnl is not None
                                else ""
                            ),
                            "FinInstrmGnlAttrbts.CmmdtyDerivInd": (
                                gnl.findtext(
                                    "a:CmmdtyDerivInd", default="", namespaces=ns
                                )
                                if gnl is not None
                                else ""
                            ),
                            "FinInstrmGnlAttrbts.NtnlCcy": (
                                gnl.findtext("a:NtnlCcy", default="", namespaces=ns)
                                if gnl is not None
                                else ""
                            ),
                            "Issr": issr,
                        }

                        records.append(row)
                    except Exception as e:
                        logger.warning(f"Error parsing FinInstrm: {e}")
                    finally:
                        elem.clear()

            df = pd.DataFrame(records)
            os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
            df.to_csv(output_csv_path, index=False)
            logger.info(f"CSV written to {output_csv_path} with {len(df)} rows")
            return output_csv_path

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise
        except Exception as e:
            logger.critical(
                f"Unexpected error during CSV conversion: {e}", exc_info=True
            )
            raise
