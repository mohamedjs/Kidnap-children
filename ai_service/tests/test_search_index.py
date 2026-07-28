import pytest
import os
import numpy as np
import tempfile
from ai_service.app.search_index import FAISSSearchIndex

def test_faiss_search_index_add_and_search():
    with tempfile.TemporaryDirectory() as tmp_dir:
        search_index = FAISSSearchIndex(dim=512, storage_dir=tmp_dir)
        
        # Generate distinct test vectors
        vec1 = np.random.randn(512).astype(np.float32)
        vec1 /= np.linalg.norm(vec1)
        
        vec2 = np.random.randn(512).astype(np.float32)
        vec2 /= np.linalg.norm(vec2)
        
        # Add embeddings for post 45 and post 12
        added1 = search_index.add_embeddings(post_id=45, embeddings=[vec1])
        added2 = search_index.add_embeddings(post_id=12, embeddings=[vec2])
        
        assert added1 == 1
        assert added2 == 1
        assert search_index.get_post_count() == 2
        assert search_index.get_vector_count() == 2
        
        # Search with vec1 (should yield post 45 as top match with ~100% confidence)
        matches = search_index.search(vec1, top_k=10)
        assert len(matches) == 2
        top_match = matches[0]
        assert top_match["post_id"] == 45
        assert top_match["confidence"] > 95.0

def test_faiss_search_index_ranking_order():
    with tempfile.TemporaryDirectory() as tmp_dir:
        search_index = FAISSSearchIndex(dim=512, storage_dir=tmp_dir)
        
        base_vec = np.random.randn(512).astype(np.float32)
        base_vec /= np.linalg.norm(base_vec)
        
        # Slightly perturbed vector for post 45 (high similarity)
        near_vec = base_vec + np.random.randn(512).astype(np.float32) * 0.05
        near_vec /= np.linalg.norm(near_vec)
        
        # Dissimilar vector for post 99
        far_vec = -base_vec + np.random.randn(512).astype(np.float32) * 0.1
        far_vec /= np.linalg.norm(far_vec)
        
        search_index.add_embeddings(post_id=45, embeddings=[near_vec])
        search_index.add_embeddings(post_id=99, embeddings=[far_vec])
        
        results = search_index.search(base_vec, top_k=2)
        assert len(results) == 2
        assert results[0]["post_id"] == 45
        assert results[1]["post_id"] == 99
        assert results[0]["confidence"] > results[1]["confidence"]

def test_faiss_index_reset():
    with tempfile.TemporaryDirectory() as tmp_dir:
        search_index = FAISSSearchIndex(dim=512, storage_dir=tmp_dir)
        vec = np.random.randn(512).astype(np.float32)
        search_index.add_embeddings(post_id=100, embeddings=[vec])
        assert search_index.get_vector_count() == 1
        
        search_index.reset()
        assert search_index.get_vector_count() == 0
        assert search_index.get_post_count() == 0
        assert search_index.search(vec) == []
