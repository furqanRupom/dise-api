import re
from dataclasses import dataclass, field
from typing import Literal

from app.integrations.barcode.base import BarcodeResult
from app.integrations.barcode.zxing import ZXingBarcodeProvider
from app.integrations.ocr.tesseract import (
    OCRCandidateResult,
    TesseractOCRProvider,
)

BarcodeStatus = Literal[
    "DECODED",
    "NOT_DECODED",
]


@dataclass
class LicenseImageResult:
    """
    Extraction result for one side of a driving licence.
    """

    image_path: str

    ocr: OCRCandidateResult | None = None

    barcodes: list[BarcodeResult] = field(
        default_factory=list,
    )

    name: str | None = None
    date_of_birth: str | None = None
    license_number: str | None = None
    authority: str | None = None

    address: str | None = None
    vehicle_classes: list[str] = field(
        default_factory=list,
    )


@dataclass
class LicenseDocumentResult:
    """
    Combined extraction result for a driving licence.

    The front side is the primary source for licence
    information.

    The back side is used for barcode detection.

    This does not prove authenticity or legal validity.
    """

    front: LicenseImageResult
    back: LicenseImageResult

    barcode_status: BarcodeStatus


class LicenseDocumentService:
    """
    Extract information from both sides of a driving licence.

    Front:
        OCR extracts licence information.

    Back:
        Barcode decoder attempts to decode barcode data.

    Barcode data is currently treated as supporting data only.
    We do not assume that the barcode contains the licence number.
    """

    def __init__(
        self,
        ocr_provider: TesseractOCRProvider | None = None,
        barcode_provider: ZXingBarcodeProvider | None = None,
    ):
        self.ocr_provider = ocr_provider or TesseractOCRProvider()

        self.barcode_provider = barcode_provider or ZXingBarcodeProvider()

    # ---------------------------------------------------------
    # Normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_license_number(
        value: str,
    ) -> str:
        """
        Normalize a licence number.

        OCR can confuse visually similar characters such as
        O and 0.
        """

        value = value.upper().strip()

        value = re.sub(
            r"[^A-Z0-9]",
            "",
            value,
        )

        return value.replace("O", "0")

    # ---------------------------------------------------------
    # Licence number extraction
    # ---------------------------------------------------------

    @classmethod
    def _extract_license_number(
        cls,
        text: str,
    ) -> str | None:
        """
        Extract a likely Bangladesh driving licence number
        from OCR text.
        """

        matches = re.findall(
            r"\bDK[A-Z0-9]{10,14}\b",
            text.upper(),
        )

        if not matches:
            return None

        return cls._normalize_license_number(
            matches[0],
        )

    # ---------------------------------------------------------
    # Name extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_name(
        text: str,
    ) -> str | None:
        """
        Extract a likely name from front-side OCR text.
        """

        match = re.search(
            r"\bNAME\.?\s+(?:[^\n|]*?\s+)?"
            r"([A-Z][A-Z ]{3,})"
            r"(?=\s+(?:C?H?OWM|DATE|DOB|BIRTH|LICEN|AUTHORITY))",
            text.upper(),
        )

        if not match:
            return None

        name = re.sub(
            r"\s+",
            " ",
            match.group(1),
        ).strip()

        return name or None

    # ---------------------------------------------------------
    # Date of birth extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_date_of_birth(
        text: str,
    ) -> str | None:
        """
        Extract date of birth.

        Example:

            21APR1992
        """

        match = re.search(
            r"\b\d{1,2}[A-Z]{3}\d{4}\b",
            text.upper(),
        )

        if not match:
            return None

        return match.group(0)

    # ---------------------------------------------------------
    # Authority extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_authority(
        text: str,
    ) -> str | None:
        """
        Extract the licensing authority.
        """

        text_upper = text.upper()

        match = re.search(
            r"\b([A-Z]+(?:\s+[A-Z]+)*\s+METRO-\d+)"
            r"\s*,?\s*BRTA\b",
            text_upper,
        )

        if match:
            return f"{match.group(1).strip()}, BRTA"

        if "BRTA" in text_upper:
            return "BRTA"

        return None

    # ---------------------------------------------------------
    # Address extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_address(
        text: str,
    ) -> str | None:
        """
        Extract an address from OCR text.

        This is supporting information only.
        """

        match = re.search(
            r"\b(?:ADDRESS|ADARESS)\s*:\s*(.+)",
            text,
            re.IGNORECASE,
        )

        if not match:
            return None

        address = match.group(1)

        address = re.split(
            r"\bCLASS\b"
            r"|\bLIGHT\b"
            r"|\bTWO\s*WHEELER\b"
            r"|\bSAME\b",
            address,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]

        address = re.sub(
            r"\s+",
            " ",
            address,
        ).strip()

        return address or None

    # ---------------------------------------------------------
    # Vehicle classes
    # ---------------------------------------------------------

    @staticmethod
    def _extract_vehicle_classes(
        text: str,
    ) -> list[str]:
        """
        Extract known vehicle classes.

        This is supporting information only.
        """

        text_upper = text.upper()

        classes: list[str] = []

        if re.search(
            r"\bLIGHT\b",
            text_upper,
        ):
            classes.append("Light")

        if re.search(
            r"\bTWO\s*WHEEL(?:ER|ERS)\b",
            text_upper,
        ):
            classes.append("Two Wheeler")

        return classes

    # ---------------------------------------------------------
    # Process front
    # ---------------------------------------------------------

    def _process_front(
        self,
        image_path: str,
    ) -> LicenseImageResult:
        """
        Process the front side using OCR.
        """

        ocr_result = self.ocr_provider.extract_best_result(
            image_path,
        )

        text = ocr_result.text

        return LicenseImageResult(
            image_path=image_path,
            ocr=ocr_result,
            name=self._extract_name(text),
            date_of_birth=self._extract_date_of_birth(
                text,
            ),
            license_number=self._extract_license_number(
                text,
            ),
            authority=self._extract_authority(
                text,
            ),
        )

    # ---------------------------------------------------------
    # Process back
    # ---------------------------------------------------------

    def _process_back(
        self,
        image_path: str,
    ) -> LicenseImageResult:
        """
        Process the back side using barcode detection.

        Back-side OCR is intentionally not used here.
        """

        barcodes = self.barcode_provider.decode(
            image_path,
        )

        return LicenseImageResult(
            image_path=image_path,
            barcodes=barcodes,
        )

    # ---------------------------------------------------------
    # Document extraction
    # ---------------------------------------------------------

    def extract(
        self,
        front_image_path: str,
        back_image_path: str,
    ) -> LicenseDocumentResult:
        """
        Extract information from both sides.

        Front:
            OCR.

        Back:
            Barcode.
        """

        front = self._process_front(
            front_image_path,
        )

        back = self._process_back(
            back_image_path,
        )

        barcode_status: BarcodeStatus = "DECODED" if back.barcodes else "NOT_DECODED"

        return LicenseDocumentResult(
            front=front,
            back=back,
            barcode_status=barcode_status,
        )
