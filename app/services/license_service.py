import re
from dataclasses import dataclass, field

from app.integrations.barcode.base import BarcodeResult
from app.integrations.barcode.zxing import ZXingBarcodeProvider
from app.integrations.ocr.tesseract import (
    OCRCandidateResult,
    TesseractOCRProvider,
)


@dataclass
class LicenseImageResult:
    """
    Extraction result for one side of a driving licence.
    """

    image_path: str
    ocr: OCRCandidateResult
    barcodes: list[BarcodeResult] = field(default_factory=list)
    license_number: str | None = None


@dataclass
class LicenseDocumentResult:
    """
    Combined extraction result for a driving licence.

    This contains extracted information only.
    It does not determine whether the licence is genuine.
    """

    front: LicenseImageResult
    back: LicenseImageResult
    license_number_match: bool = False


class LicenseDocumentService:
    """
    Extract information from the front and back of a driving licence.

    OCR and barcode decoding are intentionally kept as separate
    integrations. This service combines their results into one
    document-level result.
    """

    def __init__(
        self,
        ocr_provider: TesseractOCRProvider | None = None,
        barcode_provider: ZXingBarcodeProvider | None = None,
    ):
        self.ocr_provider = ocr_provider or TesseractOCRProvider()
        self.barcode_provider = barcode_provider or ZXingBarcodeProvider()

    @staticmethod
    def _normalize_license_number(value: str) -> str:
        """
        Normalize a licence number before comparison.

        OCR can confuse visually similar characters such as
        O and 0.
        """

        value = value.upper().strip()

        value = re.sub(r"[^A-Z0-9]", "", value)

        return value.replace("O", "0")

    @classmethod
    def _extract_license_number(
        cls,
        text: str,
    ) -> str | None:
        """
        Extract a likely Bangladesh driving licence number
        from OCR text.

        Current format observed in the sample:
            DK0899123CL0012
        """

        normalized_text = text.upper()

        matches = re.findall(
            r"\bDK[A-Z0-9]{10,14}\b",
            normalized_text,
        )

        if not matches:
            return None

        return cls._normalize_license_number(matches[0])

    def _process_image(
        self,
        image_path: str,
        *,
        detect_barcode: bool = False,
    ) -> LicenseImageResult:
        """
        Process one side of the licence.

        OCR and barcode detection are both performed when enabled.
        """

        ocr_result = self.ocr_provider.extract_best_result(image_path)

        barcodes: list[BarcodeResult] = []

        if detect_barcode:
            barcodes = self.barcode_provider.decode(image_path)

        license_number = self._extract_license_number(ocr_result.text)

        return LicenseImageResult(
            image_path=image_path,
            ocr=ocr_result,
            barcodes=barcodes,
            license_number=license_number,
        )

    def extract(
        self,
        front_image_path: str,
        back_image_path: str,
    ) -> LicenseDocumentResult:
        """
        Extract OCR, licence number, and barcode information
        from both sides.
        """

        front = self._process_image(
            front_image_path,
            detect_barcode=True,
        )

        back = self._process_image(
            back_image_path,
            detect_barcode=True,
        )

        license_number_match = (
            front.license_number is not None
            and back.license_number is not None
            and front.license_number == back.license_number
        )

        return LicenseDocumentResult(
            front=front,
            back=back,
            license_number_match=license_number_match,
        )
