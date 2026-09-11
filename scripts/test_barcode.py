import sys

from app.integrations.barcode.zxing import ZXingBarcodeProvider


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage:")
        print("  PYTHONPATH=. python scripts/test_barcode.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    barcode = ZXingBarcodeProvider()

    try:
        results = barcode.decode(image_path)

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("========== BARCODE RESULT ==========")
    print()

    if not results:
        print("No readable barcode detected.")
        print()
        print("This does NOT prove that the document has no barcode.")
        print(
            "The barcode may be unsupported, damaged, too small, "
            "or located on another side."
        )

    else:
        print(f"Detected barcodes: {len(results)}")
        print()

        for index, result in enumerate(results, start=1):
            print(f"Barcode #{index}")
            print(f"Format       : {result.format}")
            print(f"Content type : {result.content_type}")
            print(f"Text         : {result.text}")
            print()

    print("====================================")


if __name__ == "__main__":
    main()
