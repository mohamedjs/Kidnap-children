import pytest
import io
import numpy as np
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient

from ai_service.app.main import app, search_index

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_search_index():
    search_index.reset()
    yield
    search_index.reset()

def create_synthetic_image_bytes(draw_face=True):
    img = Image.new("RGB", (200, 200), color=(220, 220, 220))
    if draw_face:
        draw = ImageDraw.Draw(img)
        draw.ellipse([40, 40, 160, 160], fill=(230, 200, 180), outline=(50, 50, 50))
        draw.ellipse([65, 80, 85, 100], fill=(50, 50, 50))
        draw.ellipse([115, 80, 135, 100], fill=(50, 50, 50))
        draw.polygon([(100, 100), (95, 120), (105, 120)], fill=(180, 140, 120))
        draw.arc([75, 125, 125, 145], start=0, end=180, fill=(150, 50, 50), width=3)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "total_indexed_posts" in data
    assert "total_indexed_vectors" in data

def test_openapi_docs_endpoint():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "/api/v1/compare" in spec["paths"]
    assert "/api/v1/index" in spec["paths"]

def test_index_and_compare_workflow():
    img_bytes = create_synthetic_image_bytes(draw_face=True)
    
    # 1. Index image for post_id 45
    index_res = client.post(
        "/api/v1/index",
        data={"post_id": 45},
        files={"file": ("child45.jpg", img_bytes, "image/jpeg")}
    )
    assert index_res.status_code == 200
    idx_data = index_res.json()
    assert idx_data["status"] == "success"
    assert idx_data["post_id"] == 45
    assert idx_data["embeddings_added"] >= 1
    
    # 2. Compare uploaded image
    compare_res = client.post(
        "/api/v1/compare",
        files={"file": ("target.jpg", img_bytes, "image/jpeg")}
    )
    assert compare_res.status_code == 200
    comp_data = compare_res.json()
    assert comp_data["face_detected"] is True
    assert "matches" in comp_data
    assert len(comp_data["matches"]) >= 1
    match = comp_data["matches"][0]
    assert match["post_id"] == 45
    assert isinstance(match["confidence"], float)
    assert match["confidence"] >= 50.0

def test_compare_non_face_image():
    # Pure blank rectangle without face
    blank_img = Image.new("RGB", (300, 100), color=(0, 0, 0))
    buf = io.BytesIO()
    blank_img.save(buf, format="JPEG")
    
    res = client.post(
        "/api/v1/compare",
        files={"file": ("blank.jpg", buf.getvalue(), "image/jpeg")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["face_detected"] is False
    assert data["matches"] == []

def test_compare_missing_file():
    res = client.post("/api/v1/compare")
    assert res.status_code == 400
