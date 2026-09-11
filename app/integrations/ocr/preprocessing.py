import cv2
import numpy as np


def preprocess_image(
    image_path: str, debug_output_path: str | None = None
) -> np.ndarray:
    """
    Basic preprocessing pipeline to improve OCR accuracy.

    Steps: grayscale -> resize (upscale if small) -> contrast
    enhancement -> adaptive thresholding.

    Returns a processed image array (not a file path) that pytesseract
    can accept directly.

    If debug_output_path is provided, saves the processed image to disk
    so it can be visually inspected.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    if width < 1000:
        scale = 1000 / width
        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast_enhanced = clahe.apply(gray)

    thresholded = cv2.adaptiveThreshold(
        contrast_enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    if debug_output_path:
        cv2.imwrite(debug_output_path, thresholded)

    return thresholded
