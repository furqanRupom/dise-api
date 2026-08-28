from io import BytesIO

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

ALLOWED_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


async def upload_image(file: UploadFile) -> dict:
    # Validate MIME type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WebP images are allowed",
        )

    # Read file
    contents = await file.read()

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum file size is 5MB.",
        )

    # Validate that the file is actually an image
    try:
        image = Image.open(BytesIO(contents))
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    # Re-open because verify() invalidates the image object
    image = Image.open(BytesIO(contents))

    # Convert to RGB
    image = image.convert("RGB")

    # Resize
    image.thumbnail((500, 500))

    # Convert to JPEG
    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=85,
        optimize=True,
    )

    buffer.seek(0)

    # Upload to Cloudinary
    result = cloudinary.uploader.upload(
        buffer,
        folder=settings.CLOUDINARY_FOLDER,
        resource_type="image",
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
    }


def delete_image(url):
    cloudinary.uploader.destroy(url)
