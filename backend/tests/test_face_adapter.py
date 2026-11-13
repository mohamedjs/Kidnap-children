import pytest

from app.modules.matching.domain.scoring import cosine
from app.modules.matching.infrastructure.face import OpenCvDctFaceAnalyzer
from scripts.placeholders import silhouette


def test_rejects_non_images() -> None:
    with pytest.raises(ValueError):
        OpenCvDctFaceAnalyzer().embed(b"<html>not an image</html>")


def test_silhouette_has_no_detectable_face() -> None:
    # demo pictures are generated silhouettes on purpose: they must not look like real faces
    assert OpenCvDctFaceAnalyzer().embed(silhouette(1)) == []


def test_vector_is_deterministic_and_normalised() -> None:
    import cv2
    import numpy as np

    img = cv2.imdecode(np.frombuffer(silhouette(2), np.uint8), cv2.IMREAD_GRAYSCALE)
    v1 = OpenCvDctFaceAnalyzer._vector(img)
    v2 = OpenCvDctFaceAnalyzer._vector(img.copy())
    assert len(v1) == 255
    assert cosine(v1, v2) == pytest.approx(1.0)
    assert sum(x * x for x in v1) == pytest.approx(1.0, rel=1e-5)
