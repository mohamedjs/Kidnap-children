import pytest
import numpy as np
from PIL import Image, ImageDraw
from ai_service.app.extractor import FaceExtractor, ArcFaceEmbeddingNet
import torch

def create_synthetic_face_image(width=200, height=200, bg_color=(200, 200, 200), draw_face=True):
    img = Image.new("RGB", (width, height), color=bg_color)
    if draw_face:
        draw = ImageDraw.Draw(img)
        # Head outline
        draw.ellipse([40, 40, 160, 160], fill=(230, 200, 180), outline=(50, 50, 50))
        # Eyes
        draw.ellipse([65, 80, 85, 100], fill=(50, 50, 50))
        draw.ellipse([115, 80, 135, 100], fill=(50, 50, 50))
        # Nose
        draw.polygon([(100, 100), (95, 120), (105, 120)], fill=(180, 140, 120))
        # Mouth
        draw.arc([75, 125, 125, 145], start=0, end=180, fill=(150, 50, 50), width=3)
    return img

def test_arcface_embedding_net_output_shape_and_norm():
    net = ArcFaceEmbeddingNet(embedding_dim=512)
    net.eval()
    dummy_tensor = torch.randn(2, 3, 112, 112)
    with torch.no_grad():
        out = net(dummy_tensor)
    assert out.shape == (2, 512)
    # Check L2 normalization
    norms = torch.norm(out, p=2, dim=1).numpy()
    np.testing.assert_allclose(norms, [1.0, 1.0], rtol=1e-4)

def test_extractor_feature_extraction():
    extractor = FaceExtractor()
    img = create_synthetic_face_image(draw_face=True)
    faces = extractor.extract_faces(img)
    
    assert len(faces) >= 1
    primary = faces[0]
    assert "bbox" in primary
    assert "embedding" in primary
    assert primary["embedding"].shape == (512,)
    # Verify embedding is L2 normalized
    norm = np.linalg.norm(primary["embedding"])
    assert abs(norm - 1.0) < 1e-3

def test_extractor_non_face_image():
    extractor = FaceExtractor()
    # Pure blank noise/flat color non-face image with unequal aspect ratio
    blank_img = Image.new("RGB", (300, 100), color=(10, 10, 10))
    faces = extractor.extract_faces(blank_img)
    # Non-face image should return empty list
    assert faces == []
