import pytesseract
from PIL import Image

from app.integrations.ocr.base import OCRProvider
from app.integrations.ocr.preprocessing import preprocess_image


class TesseractOCRProvider(OCRProvider):
    """
    Local OCR provider backed by the Tesseract engine via pytesseract.

    This is a development/local provider intended to be swapped for a
    stronger provider in production. It is not a document authenticity
    check of any kind.
    """

    def __init__(self, languages: str = "eng+ben"):
        self.languages = languages

    def extract_text(self, image_path: str) -> str:
        processed_path = preprocess_image(image_path)

        try:
            image = Image.open(processed_path)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Image not found: {processed_path}") from e

        try:
            text = pytesseract.image_to_string(image, lang=self.languages)
        except pytesseract.TesseractNotFoundError as e:
            raise RuntimeError(
                "Tesseract binary not found. Make sure 'tesseract' is "
                "installed and on your PATH (pacman -S tesseract)."
            ) from e

        return text.strip()
