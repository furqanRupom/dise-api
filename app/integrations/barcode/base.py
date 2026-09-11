from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BarcodeResult:
    """
    Result returned after successfully decoding a barcode.
    """

    format: str
    text: str
    content_type: str | None = None


class BarcodeProvider(ABC):
    """
    Abstract interface for barcode decoding.

    The rest of the application should depend on this interface,
    not directly on ZXing or another barcode library.
    """

    @abstractmethod
    def decode(self, image_path: str) -> list[BarcodeResult]:
        """
        Detect and decode barcodes from an image.

        Returns:
            A list of decoded barcode results.

        An empty list means that no barcode could be decoded.
        """
        ...
