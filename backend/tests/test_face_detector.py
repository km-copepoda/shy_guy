import numpy as np

from services.face_detector import FaceDetector


class TestFaceDetector:
    def setup_method(self):
        self.detector = FaceDetector()

    def test_return_type_is_list_of_int_tuples(self, sample_rgb_image):
        faces = self.detector.detect(sample_rgb_image)
        assert isinstance(faces, list)
        for face in faces:
            assert isinstance(face, tuple)
            assert len(face) == 4
            assert all(isinstance(v, int) for v in face)

    def test_solid_color_image_returns_zero_faces(self, sample_rgb_image):
        faces = self.detector.detect(sample_rgb_image)
        assert len(faces) == 0

    def test_bounding_boxes_within_image_bounds(self, sample_rgb_image):
        h, w = sample_rgb_image.shape[:2]
        faces = self.detector.detect(sample_rgb_image)
        for x, y, fw, fh in faces:
            assert x >= 0
            assert y >= 0
            assert x + fw <= w
            assert y + fh <= h

    def test_high_threshold_returns_zero(self, sample_rgb_image):
        strict_detector = FaceDetector(score_threshold=0.99)
        faces = strict_detector.detect(sample_rgb_image)
        assert len(faces) == 0
