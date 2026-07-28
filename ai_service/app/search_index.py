import os
import json
import numpy as np
try:
    import faiss
except ImportError:
    faiss = None

class FAISSSearchIndex:
    """
    FAISS-backed vector search index for age-invariant facial embedding vectors.
    Uses IndexFlatIP on L2-normalized 512d vectors to produce exact cosine similarity scores.
    """
    def __init__(self, dim: int = 512, storage_dir: str = None):
        self.dim = dim
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.index_file = os.path.join(self.storage_dir, "faiss.index")
        self.meta_file = os.path.join(self.storage_dir, "metadata.json")
        
        self.post_ids = []  # parallel list mapping index position i -> post_id
        
        if faiss is not None:
            self.index = faiss.IndexFlatIP(self.dim)
        else:
            self.index = None
            
        self.load()

    def add_embeddings(self, post_id: int, embeddings: list[np.ndarray]) -> int:
        """
        Add one or more 512d embeddings for a given post_id.
        """
        if not embeddings:
            return 0
        
        vecs = []
        for emb in embeddings:
            vec = np.ascontiguousarray(emb, dtype=np.float32).reshape(1, -1)
            # Ensure L2 normalization
            norm = np.linalg.norm(vec, axis=1, keepdims=True)
            if norm[0, 0] > 1e-6:
                vec = vec / norm
            vecs.append(vec)
            self.post_ids.append(int(post_id))
            
        stacked = np.vstack(vecs)
        if self.index is not None:
            self.index.add(stacked)
            
        self.save()
        return len(vecs)

    def search(self, query_embedding: np.ndarray, top_k: int = 10, min_confidence: float = 0.0) -> list[dict]:
        """
        Search top_k matches for query_embedding vector.
        Returns list of dicts: [{"post_id": int, "confidence": float}, ...]
        Aggregates multiple face matches per post_id by selecting highest confidence per post.
        """
        if self.index is None or self.index.ntotal == 0 or len(self.post_ids) == 0:
            return []

        q_vec = np.ascontiguousarray(query_embedding, dtype=np.float32).reshape(1, -1)
        norm = np.linalg.norm(q_vec, axis=1, keepdims=True)
        if norm[0, 0] > 1e-6:
            q_vec = q_vec / norm

        k = min(top_k * 5, self.index.ntotal)
        distances, indices = self.index.search(q_vec, k)

        best_post_scores = {}
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.post_ids):
                continue
            post_id = self.post_ids[idx]
            # Convert cosine similarity (-1.0 to 1.0) to confidence percentage (0.0 to 100.0)
            confidence = max(0.0, min(100.0, float((dist + 1.0) / 2.0 * 100.0)))
            if confidence >= min_confidence:
                if post_id not in best_post_scores or confidence > best_post_scores[post_id]:
                    best_post_scores[post_id] = confidence

        # Sort by confidence descending
        sorted_matches = [
            {"post_id": post_id, "confidence": confidence}
            for post_id, confidence in sorted(best_post_scores.items(), key=lambda x: x[1], reverse=True)
        ]
        return sorted_matches[:top_k]

    def get_post_count(self) -> int:
        return len(set(self.post_ids))

    def get_vector_count(self) -> int:
        if self.index is not None:
            return self.index.ntotal
        return len(self.post_ids)

    def reset(self):
        self.post_ids = []
        if faiss is not None:
            self.index = faiss.IndexFlatIP(self.dim)
        if os.path.exists(self.index_file):
            os.remove(self.index_file)
        if os.path.exists(self.meta_file):
            os.remove(self.meta_file)

    def save(self):
        try:
            if self.index is not None and faiss is not None:
                faiss.write_index(self.index, self.index_file)
            with open(self.meta_file, "w") as f:
                json.dump({"post_ids": self.post_ids}, f)
        except Exception:
            pass

    def load(self):
        try:
            if os.path.exists(self.index_file) and faiss is not None:
                self.index = faiss.read_index(self.index_file)
            if os.path.exists(self.meta_file):
                with open(self.meta_file, "r") as f:
                    data = json.load(f)
                    self.post_ids = data.get("post_ids", [])
        except Exception:
            self.reset()
