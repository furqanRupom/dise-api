import sys

from app.services.license_service import (
    LicenseDocumentService,
)


def main() -> None:
    if len(sys.argv) != 3:
        print(
            "Usage: python scripts/test_license_document.py <front_image> <back_image>"
        )
        sys.exit(1)

    front_image = sys.argv[1]
    back_image = sys.argv[2]

    service = LicenseDocumentService()

    result = service.extract(
        front_image_path=front_image,
        back_image_path=back_image,
    )

    print("=" * 60)
    print("LICENSE DOCUMENT EXTRACTION RESULT")
    print("=" * 60)

    print("\n========== FRONT OCR ==========")
    print(f"Candidate   : {result.front.ocr.name}")
    print(f"Confidence  : {result.front.ocr.confidence:.2f}")
    print(f"Text        : {result.front.ocr.text}")

    print("\n========== BACK OCR ==========")
    print(f"Candidate   : {result.back.ocr.name}")
    print(f"Confidence  : {result.back.ocr.confidence:.2f}")
    print(f"Text        : {result.back.ocr.text}")

    print("\n========== BACK BARCODES ==========")

    if not result.back.barcodes:
        print("No readable barcode detected.")
    else:
        for index, barcode in enumerate(
            result.back.barcodes,
            start=1,
        ):
            print(f"\nBarcode #{index}")
            print(f"Format       : {barcode.format}")
            print(f"Content type : {barcode.content_type}")
            print(f"Text         : {barcode.text}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
