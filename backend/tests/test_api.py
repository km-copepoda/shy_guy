import io

from fastapi.testclient import TestClient
from PIL import Image

from main import app
from tests.conftest import create_test_jpg, create_test_png

client = TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestMosaicEndpoint:
    def test_jpeg_upload_success(self):
        data = create_test_jpg()
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.jpg", io.BytesIO(data), "image/jpeg")},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/jpeg"

    def test_png_upload_success(self):
        data = create_test_png()
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_returned_image_is_downloadable_and_same_size(self):
        data = create_test_png(200, 150)
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert response.status_code == 200
        result_img = Image.open(io.BytesIO(response.content))
        assert result_img.size == (200, 150)

    def test_unsupported_format_returns_400(self):
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.gif", io.BytesIO(b"fake"), "image/gif")},
        )
        assert response.status_code == 400

    def test_broken_data_returns_400(self):
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.jpg", io.BytesIO(b"not-an-image"), "image/jpeg")},
        )
        assert response.status_code == 400

    def test_pixel_size_valid_range(self):
        data = create_test_png()
        # Valid: pixel_size=1
        resp = client.post(
            "/api/mosaic?pixel_size=1",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert resp.status_code == 200

        # Valid: pixel_size=100
        data = create_test_png()
        resp = client.post(
            "/api/mosaic?pixel_size=100",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert resp.status_code == 200

    def test_pixel_size_zero_returns_422(self):
        data = create_test_png()
        resp = client.post(
            "/api/mosaic?pixel_size=0",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert resp.status_code == 422

    def test_pixel_size_negative_returns_422(self):
        data = create_test_png()
        resp = client.post(
            "/api/mosaic?pixel_size=-1",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert resp.status_code == 422

    def test_pixel_size_101_returns_422(self):
        data = create_test_png()
        resp = client.post(
            "/api/mosaic?pixel_size=101",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert resp.status_code == 422

    def test_pixel_size_102_returns_422(self):
        data = create_test_png()
        resp = client.post(
            "/api/mosaic?pixel_size=102",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert resp.status_code == 422

    def test_x_faces_detected_header_is_numeric(self):
        data = create_test_png()
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert response.status_code == 200
        header_val = response.headers.get("x-faces-detected")
        assert header_val is not None
        assert header_val.isdigit()

    def test_solid_image_zero_faces(self):
        data = create_test_png()
        response = client.post(
            "/api/mosaic",
            files={"file": ("test.png", io.BytesIO(data), "image/png")},
        )
        assert response.status_code == 200
        assert response.headers.get("x-faces-detected") == "0"
