import io
import logging

import numpy as np
from fastapi import APIRouter, Query, Request, UploadFile
from fastapi.responses import Response
from PIL import Image

from services.mosaic_processor import apply_mosaic

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/mosaic")
async def create_mosaic(
    request: Request,
    file: UploadFile,
    pixel_size: int = Query(default=20, ge=1, le=100),
):
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        return Response(
            content="Unsupported image format. Use JPEG, PNG, or WebP.",
            status_code=400,
        )

    # Read and validate file size
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        return Response(
            content="File too large. Maximum size is 10MB.",
            status_code=413,
        )

    # Decode image with Pillow
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        logger.exception("Failed to decode image")
        return Response(content="Invalid image data.", status_code=400)

    # Detect faces
    image_np = np.array(image)
    face_detector = request.app.state.face_detector
    faces = face_detector.detect(image_np)
    logger.info("Detected %d face(s), pixel_size=%d", len(faces), pixel_size)

    # Apply mosaic
    result_image = apply_mosaic(image, faces, pixel_size)

    # Determine output format based on input
    is_png = file.content_type == "image/png"
    output_buf = io.BytesIO()
    if is_png:
        result_image.save(output_buf, format="PNG")
        media_type = "image/png"
    else:
        result_image.save(output_buf, format="JPEG", quality=90)
        media_type = "image/jpeg"

    return Response(
        content=output_buf.getvalue(),
        media_type=media_type,
        headers={"X-Faces-Detected": str(len(faces))},
    )
