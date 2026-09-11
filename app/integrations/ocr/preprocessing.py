"""
Image preprocessing for OCR.

This is intentionally a no-op passthrough for now. The real preprocessing
pipeline (grayscale, resize, contrast enhancement, thresholding) is built
in Phase 3, once we've confirmed raw OCR works end-to-end without it.
Keeping this as its own module now means Phase 3 only has to touch this
one file.
"""


def preprocess_image(image_path: str) -> str:
    """
    Placeholder preprocessing step.

    Currently returns the image path unchanged. In Phase 3 this will load
    the image, apply OpenCV preprocessing, and return a path to a
    processed temporary image instead.
    """
    return image_path
