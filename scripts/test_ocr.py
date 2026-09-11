import sys

from app.integrations.ocr.tesseract import TesseractOCRProvider


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python scripts/test_ocr.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    ocr = TesseractOCRProvider()

    try:
        text = ocr.extract_text(image_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("========== OCR RESULT ==========")
    print()
    print(text)
    print()
    print("================================")


if __name__ == "__main__":
    main()
