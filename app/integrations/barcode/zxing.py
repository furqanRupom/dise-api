import cv2
import zxingcpp

from app.integrations.barcode.base import (
    BarcodeProvider,
    BarcodeResult,
)


class ZXingBarcodeProvider(BarcodeProvider):
    """
    Barcode provider backed by ZXing-C++.

    ZXing supports multiple barcode formats including QR Code,
    PDF417, Code 128, Data Matrix, and others.

    This class only detects and decodes barcode data.

    It does NOT determine whether the barcode or document is genuine.
    """

    def decode(
        self,
        image_path: str,
    ) -> list[BarcodeResult]:
        """
        Detect and decode barcodes from an image.

        Args:
            image_path: Path to the document image.

        Returns:
            A list of decoded barcode results.

        Raises:
            FileNotFoundError:
                If the image cannot be loaded.
        """

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")

        results = zxingcpp.read_barcodes(image)

        decoded: list[BarcodeResult] = []

        for result in results:
            if not result.text:
                continue

            decoded.append(
                BarcodeResult(
                    format=str(result.format),
                    text=result.text,
                    content_type=str(result.content_type),
                )
            )

        return decoded
