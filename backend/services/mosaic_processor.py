from PIL import Image


def apply_mosaic(
    image: Image.Image,
    faces: list[tuple[int, int, int, int]],
    pixel_size: int = 20,
) -> Image.Image:
    """Apply pixelated mosaic to detected face regions.

    Args:
        image: Source PIL Image (not modified).
        faces: List of (x, y, w, h) bounding boxes.
        pixel_size: Mosaic block size. Larger = stronger mosaic.

    Returns:
        A new Image with mosaic applied to face regions.
    """
    result = image.copy()

    for x, y, w, h in faces:
        # Crop face region
        box = (x, y, x + w, y + h)
        region = result.crop(box)

        # Compute the small size (at least 1×1)
        small_w = max(1, w // pixel_size)
        small_h = max(1, h // pixel_size)

        # Shrink then enlarge to create pixelation effect
        region = region.resize((small_w, small_h), Image.BILINEAR)
        region = region.resize((w, h), Image.NEAREST)

        # Paste back
        result.paste(region, (x, y))

    return result
