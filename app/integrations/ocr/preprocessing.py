"""
OCR image preprocessing utilities.

This module provides multiple image preparation strategies for OCR.

Different documents can respond differently to preprocessing. Therefore,
we do not assume that grayscale, contrast enhancement, or thresholding
will always improve OCR accuracy.

The available preprocessing strategies are:

- Original image: keeps the image unchanged.
- Grayscale: converts the image to grayscale.
- Thresholded: upscales small images, enhances contrast with CLAHE,
  and applies adaptive thresholding.

The OCR provider can run OCR against multiple candidates and select the
most suitable result based on OCR confidence.

These functions only prepare images for OCR. They do not extract,
validate, or verify license information and they do not determine
whether a document is genuine.
"""

import os

import cv2
import numpy as np


def load_image(image_path: str) -> np.ndarray:
    """
    Load an image from disk using OpenCV.

    Args:
        image_path: Path to the input image.

    Returns:
        The loaded image as an OpenCV BGR NumPy array.

    Raises:
        FileNotFoundError: If the image cannot be loaded.
    """
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    return image


def prepare_original(image: np.ndarray) -> np.ndarray:
    """
    Return the original image without preprocessing.

    The original image is kept as an OCR candidate because some
    documents produce better OCR results without preprocessing.

    Args:
        image: OpenCV image array.

    Returns:
        The original image unchanged.
    """
    return image


def prepare_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert an image from BGR color to grayscale.

    Grayscale can simplify the image while preserving more information
    than aggressive thresholding.

    Args:
        image: OpenCV BGR image array.

    Returns:
        A grayscale image array.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def prepare_thresholded(image: np.ndarray) -> np.ndarray:
    """
    Prepare an image using an OCR-oriented thresholding pipeline.

    Steps:
        1. Convert the image to grayscale.
        2. Upscale the image if its width is below 1500 pixels.
        3. Enhance local contrast using CLAHE.
        4. Apply adaptive Gaussian thresholding.

    This preprocessing method is only one OCR candidate. It should not
    be assumed to produce better results for every document.

    Args:
        image: OpenCV BGR image array.

    Returns:
        A thresholded image suitable for OCR processing.
    """
    gray = prepare_grayscale(image)

    height, width = gray.shape

    if width < 1500:
        scale = 1500 / width

        gray = cv2.resize(
            gray,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8),
    )

    enhanced = clahe.apply(gray)

    thresholded = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=15,
    )

    return thresholded


def get_ocr_candidates(
    image_path: str,
    debug_directory: str | None = None,
) -> dict[str, np.ndarray]:
    """
    Generate multiple image candidates for OCR.

    The candidates include the original, grayscale, and thresholded
    versions of the input document.

    If a debug directory is provided, each generated candidate is
    saved as a PNG file so the preprocessing results can be inspected
    visually.

    Args:
        image_path: Path to the input document image.
        debug_directory: Optional directory where generated OCR
            candidate images will be saved.

    Returns:
        A dictionary mapping candidate names to processed image arrays.

    Raises:
        FileNotFoundError: If the input image cannot be loaded.
    """
    image = load_image(image_path)

    candidates = {
        "original": prepare_original(image),
        "grayscale": prepare_grayscale(image),
        "thresholded": prepare_thresholded(image),
    }

    if debug_directory:
        os.makedirs(
            debug_directory,
            exist_ok=True,
        )

        for name, candidate in candidates.items():
            output_path = os.path.join(
                debug_directory,
                f"{name}.png",
            )

            cv2.imwrite(
                output_path,
                candidate,
            )

    return candidates
