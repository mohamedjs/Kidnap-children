from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query, status
from typing import Optional
import io
from PIL import Image

from .extractor import FaceExtractor
from .search_index import FAISSSearchIndex
from .schemas import CompareResponse, IndexResponse, HealthResponse, MatchResult, IndexResetResponse

app = FastAPI(
    title="Kidnap-Children AI Image Recognition Microservice",
    description="Standalone Python microservice built with FastAPI, PyTorch, OpenCV, and FAISS for facial embedding extraction and similarity comparison.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

extractor = FaceExtractor()
search_index = FAISSSearchIndex(dim=512)

@app.get("/health", response_model=HealthResponse, tags=["Health"])
@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    return HealthResponse(
        status="ok",
        service="Kidnap-Children AI Image Recognition Microservice",
        version="1.0.0",
        total_indexed_posts=search_index.get_post_count(),
        total_indexed_vectors=search_index.get_vector_count()
    )

@app.post("/api/v1/compare", response_model=CompareResponse, tags=["Recognition"])
async def compare_face(
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None),
    top_k: int = Query(10, ge=1, le=100, description="Maximum number of top matching posts to return"),
    min_confidence: float = Query(0.0, ge=0.0, le=100.0, description="Minimum confidence threshold percentage")
):
    """
    Accepts an uploaded target child image, extracts deep 512d facial embeddings,
    compares against indexed post images using FAISS vector search, and returns
    sorted match results with confidence percentages (0-100%).
    """
    upload = file or image
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file supplied. Provide an image in the 'file' or 'image' field."
        )

    contents = await upload.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decode image file: {str(e)}"
        )

    faces = extractor.extract_faces(pil_image)
    if not faces:
        return CompareResponse(
            matches=[],
            face_detected=False,
            message="No face detected in the uploaded image."
        )

    primary_embedding = faces[0]["embedding"]
    raw_matches = search_index.search(primary_embedding, top_k=top_k, min_confidence=min_confidence)

    matches = [
        MatchResult(post_id=m["post_id"], confidence=round(m["confidence"], 1))
        for m in raw_matches
    ]

    return CompareResponse(
        matches=matches,
        face_detected=True,
        message=f"Successfully extracted face embedding and compared against {search_index.get_vector_count()} indexed vectors."
    )

@app.post("/api/v1/index", response_model=IndexResponse, tags=["Indexing"])
async def index_post_image(
    post_id: int = Form(..., description="ID of the post to associate with this face image"),
    file: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Indexes a post's image into the FAISS vector database.
    Extracts face embeddings and links them to post_id.
    """
    upload = file or image
    if not upload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file supplied."
        )

    contents = await upload.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decode image file: {str(e)}"
        )

    faces = extractor.extract_faces(pil_image)
    if not faces:
        return IndexResponse(
            status="skipped",
            post_id=post_id,
            embeddings_added=0,
            message="No face detected; image was skipped from index."
        )

    embeddings = [f["embedding"] for f in faces]
    added = search_index.add_embeddings(post_id, embeddings)

    return IndexResponse(
        status="success",
        post_id=post_id,
        embeddings_added=added,
        message=f"Successfully indexed {added} face embedding(s) for post {post_id}."
    )

@app.post("/api/v1/index/reset", response_model=IndexResetResponse, tags=["Indexing"])
def reset_index():
    """
    Resets and clears the FAISS index database.
    """
    search_index.reset()
    return IndexResetResponse(status="success", message="FAISS index reset successfully.")
