from pydantic import BaseModel, Field
from typing import List, Optional

class MatchResult(BaseModel):
    post_id: int = Field(..., description="ID of the matching missing/found child post")
    confidence: float = Field(..., description="Similarity confidence score as a percentage (0.0 - 100.0)")

class CompareResponse(BaseModel):
    matches: List[MatchResult] = Field(default_factory=list, description="List of matching post IDs sorted by confidence")
    face_detected: bool = Field(True, description="Whether a face was detected in the input image")
    message: Optional[str] = Field(None, description="Optional informational or status message")

class IndexRequest(BaseModel):
    post_id: int = Field(..., description="Post ID to associate with the uploaded image embedding")

class IndexResponse(BaseModel):
    status: str = Field(..., description="Status of the indexing operation ('success' or 'skipped')")
    post_id: int = Field(..., description="Post ID that was processed")
    embeddings_added: int = Field(..., description="Number of face embeddings added to the search index")
    message: Optional[str] = Field(None, description="Optional informational message")

class IndexResetResponse(BaseModel):
    status: str
    message: str

class HealthResponse(BaseModel):
    status: str = Field("ok", description="Service health status")
    service: str = Field("Kidnap-Children AI Image Recognition Microservice", description="Service name")
    version: str = Field("1.0.0", description="API version")
    total_indexed_posts: int = Field(0, description="Total unique posts indexed")
    total_indexed_vectors: int = Field(0, description="Total face vectors in FAISS index")
