import numpy as np
from PIL import Image

from services.mosaic_processor import apply_mosaic


class TestMosaicProcessor:
    def test_original_image_not_modified(self, sample_pil_image):
        original_data = list(sample_pil_image.getdata())
        faces = [(10, 10, 30, 30)]
        apply_mosaic(sample_pil_image, faces, pixel_size=10)
        assert list(sample_pil_image.getdata()) == original_data

    def test_output_size_unchanged(self, sample_pil_image):
        faces = [(10, 10, 30, 30)]
        result = apply_mosaic(sample_pil_image, faces, pixel_size=10)
        assert result.size == sample_pil_image.size

    def test_mosaic_produces_approximate_average_color(self):
        """On a gradient image, mosaic should produce colors close to the region average."""
        width, height = 100, 100
        img = Image.new("RGB", (width, height))
        pixels = img.load()
        for y in range(height):
            for x in range(width):
                pixels[x, y] = (x * 2, x * 2, x * 2)

        faces = [(20, 20, 60, 60)]
        result = apply_mosaic(img, faces, pixel_size=20)

        # The mosaic region should have colors close to the average of the gradient
        region = result.crop((20, 20, 80, 80))
        region_np = np.array(region)
        mean_val = region_np.mean()

        # Original gradient in [20..79]*2 -> mean ~99
        # Mosaic should be roughly in that range
        assert 50 < mean_val < 150

    def test_non_face_region_unchanged(self, sample_pil_image):
        faces = [(50, 50, 30, 30)]
        result = apply_mosaic(sample_pil_image, faces, pixel_size=10)

        # Check a region outside the face box
        original_pixel = sample_pil_image.getpixel((0, 0))
        result_pixel = result.getpixel((0, 0))
        assert original_pixel == result_pixel

    def test_pixel_size_one(self, sample_pil_image):
        faces = [(10, 10, 30, 30)]
        result = apply_mosaic(sample_pil_image, faces, pixel_size=1)
        assert result.size == sample_pil_image.size

    def test_large_pixel_size(self, sample_pil_image):
        faces = [(10, 10, 30, 30)]
        result = apply_mosaic(sample_pil_image, faces, pixel_size=100)
        assert result.size == sample_pil_image.size

    def test_tiny_face_region_no_crash(self):
        """Face region smaller than pixel_size should not crash."""
        img = Image.new("RGB", (100, 100), color=(200, 200, 200))
        faces = [(10, 10, 1, 1)]
        result = apply_mosaic(img, faces, pixel_size=20)
        assert result.size == img.size

    def test_empty_faces_returns_copy(self, sample_pil_image):
        result = apply_mosaic(sample_pil_image, [], pixel_size=10)
        assert result.size == sample_pil_image.size
        assert list(result.getdata()) == list(sample_pil_image.getdata())
