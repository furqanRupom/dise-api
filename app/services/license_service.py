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


@dataclass
class LicenseDocumentResult:
    """
    Combined extraction result for a driving licence.

    This contains extracted information only.
    It does not determine whether the licence is genuine.
    """

    front: LicenseImageResult
    back: LicenseImageResult


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

    def _process_image(
        self,
        image_path: str,
        *,
        detect_barcode: bool = False,
    ) -> LicenseImageResult:
        """
        Process one side of the licence.

        OCR always runs.

        Barcode detection is optional because we currently expect
        the barcode to be on the back side.
        """

        ocr_result = self.ocr_provider.extract_best_result(image_path)

        barcodes: list[BarcodeResult] = []

        if detect_barcode:
            barcodes = self.barcode_provider.decode(image_path)

        return LicenseImageResult(
            image_path=image_path,
            ocr=ocr_result,
            barcodes=barcodes,
        )

    def extract(
        self,
        front_image_path: str,
        back_image_path: str,
    ) -> LicenseDocumentResult:
        """
        Extract OCR and barcode information from both sides.

        Args:
            front_image_path: Path to the front image.
            back_image_path: Path to the back image.

        Returns:
            Combined extraction result.
        """

        front = self._process_image(
            front_image_path,
            detect_barcode=True,
        )

        back = self._process_image(
            back_image_path,
            detect_barcode=True,
        )

        return LicenseDocumentResult(
            front=front,
            back=back,
        )
