import sys

from app.integrations.ocr.tesseract import TesseractOCRProvider


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage:")
        print("  PYTHONPATH=. python scripts/test_ocr.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    ocr = TesseractOCRProvider(
        languages="eng+ben",
        psm=3,
    )

    try:
        result = ocr.extract_best_result(image_path)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("========== OCR CANDIDATE RESULT ==========")
    print()
    print(f"Best candidate : {result.name}")
    print(f"Confidence     : {result.confidence:.2f}")
    print()
    print(result.text)
    print()
    print("===========================================")


if __name__ == "__main__":
    main()
