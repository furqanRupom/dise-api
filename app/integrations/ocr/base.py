from abc import ABC, abstractmethod


class OCRProvider(ABC):
    """
    Abstract interface for text extraction from an image.

    This exists so the underlying OCR engine (local Tesseract now, a
    commercial/cloud OCR provider later) can be swapped without touching
    any code that calls it. Nothing outside app/integrations/ocr should
    import a specific provider directly — always depend on this interface.
    """

    @abstractmethod
    def extract_text(self, image_path: str) -> str:
        """
        Extract raw text from an image file.

        This performs text extraction only. It does not validate, parse,
        or verify the content, and it does not confirm the document
        is genuine.
        """
        ...
