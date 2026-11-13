"""Face analysis adapter (the v1 `ai_service`, now inside the monolith and run by the worker).

v1 used OpenCV Haar detection + a PyTorch "ArcFace" net that was never trained (random
weights), so its scores were noise. v2 keeps the same pipeline - detect, crop, embed,
cosine compare - with an honest, deterministic embedder:

  * detection: OpenCV Haar cascade (same as v1); the largest faces are kept
  * embedding: 64x64 equalised grayscale crop -> 2-D DCT -> low-frequency 16x16 block
    (minus the DC term), L2-normalised -> 255 floats

It reliably recognises the *same* photo or near-duplicates (re-posts, crops, re-encodes).
It is NOT an age-invariant face recogniser. Swapping in a trained model (e.g. an ArcFace
ONNX file run with onnxruntime) only means another FaceAnalyzer with the same `embed`.
"""

from functools import lru_cache

import cv2
import numpy as np

from app.modules.matching.domain.match import FaceAnalyzer

MAX_FACES = 3


@lru_cache
def _cascade() -> cv2.CascadeClassifier:
    path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"  # type: ignore[attr-defined]
    cascade = cv2.CascadeClassifier(path)
    if cascade.empty():
        raise RuntimeError("OpenCV face cascade not available")
    return cascade


class OpenCvDctFaceAnalyzer(FaceAnalyzer):
    model = "opencv-haar+dct-v1"

    def embed(self, image: bytes) -> list[list[float]]:
        img = cv2.imdecode(np.frombuffer(image, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("not a decodable image")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        scale = 640 / max(h, w) if max(h, w) > 640 else 1.0
        if scale != 1.0:
            gray = cv2.resize(gray, (int(w * scale), int(h * scale)))
        eq = cv2.equalizeHist(gray)
        faces = _cascade().detectMultiScale(eq, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
        if len(faces) == 0:
            return []
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[:MAX_FACES]
        return [self._vector(eq[y : y + fh, x : x + fw]) for (x, y, fw, fh) in faces]

    @staticmethod
    def _vector(crop: np.ndarray) -> list[float]:
        face = cv2.resize(crop, (64, 64)).astype(np.float32) / 255.0
        coeffs = cv2.dct(face)[:16, :16].flatten()[1:]
        norm = float(np.linalg.norm(coeffs))
        return [float(v) for v in (coeffs / norm if norm > 1e-9 else coeffs)]
