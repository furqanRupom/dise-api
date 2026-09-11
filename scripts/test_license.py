import sys

from app.services.license_service import (
    LicenseDocumentService,
)


def print_barcodes(
    barcodes,
) -> None:
    """
    Print decoded barcodes.
    """

    print("\n========== BACK BARCODES ==========")

    if not barcodes:
        print("No readable barcode detected.")
        return

    for index, barcode in enumerate(
        barcodes,
        start=1,
    ):
        print(f"\nBarcode #{index}")
        print(f"Format       : {barcode.format}")
        print(f"Content type : {barcode.content_type}")
        print(f"Text         : {barcode.text}")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python scripts/test_license.py <front_image> <back_image>")
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

    # ---------------------------------------------------------
    # Front
    # ---------------------------------------------------------

    print("\n========== FRONT OCR ==========")

    if result.front.ocr:
        print(f"Candidate      : {result.front.ocr.name}")

        print(f"Confidence     : {result.front.ocr.confidence:.2f}")

        print(f"Text           : {result.front.ocr.text}")

    print(f"Name           : {result.front.name}")

    print(f"Date of Birth  : {result.front.date_of_birth}")

    print(f"License Number : {result.front.license_number}")

    print(f"Authority      : {result.front.authority}")

    # ---------------------------------------------------------
    # Back
    # ---------------------------------------------------------

    print("\n========== BACK ==========")

    print(f"Barcode Status : {result.barcode_status}")

    print_barcodes(
        result.back.barcodes,
    )

    # ---------------------------------------------------------
    # Final
    # ---------------------------------------------------------

    print("\n========== DOCUMENT STATUS ==========")

    print(f"Front OCR      : {'AVAILABLE' if result.front.ocr else 'UNAVAILABLE'}")

    print(
        "License Number : "
        f"{'EXTRACTED' if result.front.license_number else 'NOT FOUND'}"
    )

    print(
        f"Date of Birth  : {'EXTRACTED' if result.front.date_of_birth else 'NOT FOUND'}"
    )

    print(f"Barcode        : {result.barcode_status}")

    print(
        "\nNote: This extraction does not prove "
        "document authenticity or legal validity."
    )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
