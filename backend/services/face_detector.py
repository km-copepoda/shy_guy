import logging
import os
import urllib.request

import cv2
import numpy as np

logger = logging.getLogger(__name__)

MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_detection_yunet/face_detection_yunet_2023mar.onnx"
)
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "face_detection_yunet_2023mar.onnx")


def ensure_model() -> str:
    """Download the YuNet ONNX model if it doesn't exist locally."""
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    os.makedirs(MODEL_DIR, exist_ok=True)
    logger.info("Downloading YuNet model to %s ...", MODEL_PATH)
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    logger.info("Download complete.")
    return MODEL_PATH


class FaceDetector:
    def __init__(
        self,
        score_threshold: float = 0.5,
        nms_threshold: float = 0.3,
    ):
        self.model_path = ensure_model()
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold

    def detect(
        self,
        image_np: np.ndarray,
        score_threshold: float | None = None,
    ) -> list[tuple[int, int, int, int]]:
        """Detect faces in an RGB numpy array.

        Returns a list of (x, y, w, h) integer tuples.
        """
        h, w = image_np.shape[:2]
        threshold = score_threshold if score_threshold is not None else self.score_threshold

        detector = cv2.FaceDetectorYN.create(
            self.model_path,
            "",
            (w, h),
            threshold,
            self.nms_threshold,
        )

        # YuNet expects BGR input
        bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        _, faces = detector.detect(bgr)

        if faces is None:
            return []

        results: list[tuple[int, int, int, int]] = []
        for face in faces:
            x, y, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
            # Clip to image bounds
            x = max(0, x)
            y = max(0, y)
            fw = min(fw, w - x)
            fh = min(fh, h - y)
            if fw > 0 and fh > 0:
                results.append((x, y, fw, fh))

        logger.info("Detected %d face(s)", len(results))
        return results
