# Kidnap-Children AI Image Recognition Microservice

Standalone Python-based microservice for age-invariant facial feature extraction, face recognition, and similarity matching.

## Stack & Architecture
- **Framework**: FastAPI (Async REST API with auto OpenAPI docs)
- **Deep Learning Model**: PyTorch ArcFace 512-dimensional normalized embedding model
- **Face Detection**: OpenCV Haar Cascade / DNN Detector
- **Vector Search Engine**: FAISS (`IndexFlatIP` L2-normalized cosine similarity search)

## API Endpoints

### 1. Compare Face
- **Endpoint**: `POST /api/v1/compare`
- **Payload**: `multipart/form-data` with `file` (or `image`)
- **Response**:
```json
{
  "matches": [
    {
      "post_id": 45,
      "confidence": 96.4
    },
    {
      "post_id": 12,
      "confidence": 91.8
    }
  ],
  "face_detected": true,
  "message": "Successfully extracted face embedding and compared against indexed vectors."
}
```

### 2. Index Post Image
- **Endpoint**: `POST /api/v1/index`
- **Payload**: `form-data` with `post_id` (integer) and `file` (image file)
- **Response**:
```json
{
  "status": "success",
  "post_id": 45,
  "embeddings_added": 1,
  "message": "Successfully indexed 1 face embedding(s) for post 45."
}
```

### 3. Health Check
- **Endpoint**: `GET /api/v1/health`
- **Response**:
```json
{
  "status": "ok",
  "service": "Kidnap-Children AI Image Recognition Microservice",
  "version": "1.0.0",
  "total_indexed_posts": 2,
  "total_indexed_vectors": 2
}
```

## Running locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open API documentation interactive UI: `http://localhost:8000/docs`

## Running Tests

```bash
PYTHONPATH=. pytest ai_service/tests/
```
