"""
Tesseract OCR provider.

This module provides a local OCR implementation using the Tesseract
OCR engine through pytesseract.

The provider supports multiple image preprocessing candidates because
different document images can produce different OCR results.

This module performs text extraction only. It does not determine
whether a driving license is genuine, authentic, valid, or legally
issued.
"""

from dataclasses import dataclass

import pytesseract
from PIL import Image
from pytesseract import Output

from app.integrations.ocr.base import OCRProvider
from app.integrations.ocr.preprocessing import get_ocr_candidates


@dataclass
class OCRCandidateResult:
    """
    Result produced by one OCR candidate.

    Attributes:
        name: Name of the preprocessing candidate.
        text: Text extracted by Tesseract.
        confidence: Average OCR confidence reported by Tesseract.
    """

    name: str
    text: str
    confidence: float


class TesseractOCRProvider(OCRProvider):
    """
    Local OCR provider backed by Tesseract.

    Multiple image candidates can be tested because preprocessing that
    helps one document can reduce OCR accuracy for another document.

    The original image is therefore included as an OCR candidate.

    This provider performs OCR only. It does not validate license
    information or verify document authenticity.
    """

    def __init__(
        self,
        languages: str = "eng+ben",
        psm: int = 3,
    ):
        """
        Initialize the Tesseract OCR provider.

        Args:
            languages: Tesseract language configuration.
            psm: Tesseract Page Segmentation Mode.
        """
        self.languages = languages
        self.psm = psm

    def _extract_from_image(
        self,
        image,
    ) -> tuple[str, float]:
        """
        Run Tesseract OCR on a single image.

        Tesseract's image_to_data API is used so that word-level
        confidence values can be collected.

        Args:
            image: Image array accepted by PIL/OpenCV.

        Returns:
            A tuple containing:
                - extracted text
                - average OCR confidence
        """
        try:
            pil_image = Image.fromarray(image)

            data = pytesseract.image_to_data(
                pil_image,
                lang=self.languages,
                config=f"--psm {self.psm}",
                output_type=Output.DICT,
            )

        except pytesseract.TesseractNotFoundError as e:
            raise RuntimeError(
                "Tesseract binary not found. Make sure 'tesseract' "
                "is installed and available on your PATH."
            ) from e

        words: list[str] = []
        confidences: list[float] = []

        for text, confidence in zip(
            data["text"],
            data["conf"],
        ):
            text = text.strip()

            if not text:
                continue

            try:
                confidence_value = float(confidence)
            except (TypeError, ValueError):
                continue

            if confidence_value < 0:
                continue

            words.append(text)
            confidences.append(confidence_value)

        text = " ".join(words).strip()

        if not confidences:
            return text, 0.0

        average_confidence = sum(confidences) / len(confidences)

        return text, average_confidence

    def extract_text(
        self,
        image_path: str,
    ) -> str:
        """
        Extract text from a document image.

        Multiple image candidates are generated and processed by
        Tesseract. The candidate with the highest average OCR
        confidence is returned.

        Args:
            image_path: Path to the input document image.

        Returns:
            Extracted OCR text.

        Raises:
            FileNotFoundError: If the image cannot be loaded.
            RuntimeError: If Tesseract is not installed or cannot run.
        """
        candidates = get_ocr_candidates(image_path)

        results: list[OCRCandidateResult] = []

        for name, image in candidates.items():
            text, confidence = self._extract_from_image(image)

            if text:
                results.append(
                    OCRCandidateResult(
                        name=name,
                        text=text,
                        confidence=confidence,
                    )
                )

        if not results:
            return ""

        best_result = max(
            results,
            key=lambda result: result.confidence,
        )

        return best_result.text

    def extract_best_result(
        self,
        image_path: str,
    ) -> OCRCandidateResult:
        """
        Extract OCR using all available image candidates.

        This method is useful during development because it exposes
        which preprocessing candidate produced the highest Tesseract
        confidence.

        Args:
            image_path: Path to the input document image.

        Returns:
            The OCR result with the highest average confidence.

        Raises:
            FileNotFoundError: If the image cannot be loaded.
            RuntimeError: If Tesseract is not installed or cannot run.
        """
        candidates = get_ocr_candidates(image_path)

        results: list[OCRCandidateResult] = []

        for name, image in candidates.items():
            text, confidence = self._extract_from_image(image)

            results.append(
                OCRCandidateResult(
                    name=name,
                    text=text,
                    confidence=confidence,
                )
            )

        return max(
            results,
            key=lambda result: result.confidence,
        )
