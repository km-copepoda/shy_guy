import io

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def sample_rgb_image() -> np.ndarray:
    """100x100 solid-color RGB numpy array."""
    return np.full((100, 100, 3), fill_value=128, dtype=np.uint8)


@pytest.fixture
def sample_pil_image() -> Image.Image:
    """100x100 solid-color PIL Image."""
    return Image.new("RGB", (100, 100), color=(128, 128, 128))


def create_test_png(width: int = 100, height: int = 100, color=(128, 128, 128)) -> bytes:
    """Generate PNG image bytes for testing."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_test_jpg(width: int = 100, height: int = 100, color=(128, 128, 128)) -> bytes:
    """Generate JPEG image bytes for testing."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
