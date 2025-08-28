"""Tests for retrieval functionality."""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from talktotube.utils.retrieval import EmbeddingRetriever
from talktotube.utils.text import TranscriptChunk


class TestEmbeddingRetriever:
    """Test cases for EmbeddingRetriever."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('talktotube.utils.retrieval.InferenceClient'):
            self.retriever = EmbeddingRetriever()
    
    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical vectors."""
        vec1 = np.array([1, 2, 3])
        vec2 = np.array([1, 2, 3])
        similarity = self.retriever.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-6
    
    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors."""
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([0, 1, 0])
        similarity = self.retriever.cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 1e-6
    
    def test_cosine_similarity_opposite(self):
        """Test cosine similarity with opposite vectors."""
        vec1 = np.array([1, 2, 3])
        vec2 = np.array([-1, -2, -3])
        similarity = self.retriever.cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 1e-6
    
    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        vec1 = np.array([1, 2, 3])
        vec2 = np.array([0, 0, 0])
        similarity = self.retriever.cosine_similarity(vec1, vec2)
        assert similarity == 0.0
    
    @patch.object(EmbeddingRetriever, 'get_embedding')
    def test_find_similar_chunks_basic(self, mock_get_embedding):
        """Test basic similar chunk finding."""
        # Create test chunks
        chunks = [
            TranscriptChunk("This is about cats", 0, 10, 0),
            TranscriptChunk("This discusses dogs", 10, 20, 1),
            TranscriptChunk("Weather is nice today", 20, 30, 2)
        ]
        
        # Mock embeddings
        query_embedding = np.array([1, 0, 0])
        chunk_embeddings = [
            np.array([0.9, 0.1, 0]),  # High similarity to query
            np.array([0.1, 0.9, 0]),  # Low similarity to query
            np.array([0, 0, 1])       # No similarity to query
        ]
        
        mock_get_embedding.return_value = query_embedding
        
        # Test retrieval
        results = self.retriever.find_similar_chunks(
            "cats", chunks, chunk_embeddings, top_k=2, threshold=0.5
        )
        
        assert len(results) == 1  # Only one chunk above threshold
        assert results[0][0].text == "This is about cats"
        assert results[0][1] > 0.5
    
    @patch.object(EmbeddingRetriever, 'get_embedding')
    def test_find_similar_chunks_no_results_above_threshold(self, mock_get_embedding):
        """Test finding similar chunks when none meet threshold."""
        chunks = [
            TranscriptChunk("Completely different topic", 0, 10, 0)
        ]
        
        query_embedding = np.array([1, 0, 0])
        chunk_embeddings = [np.array([0, 0, 1])]  # Low similarity
        
        mock_get_embedding.return_value = query_embedding
        
        results = self.retriever.find_similar_chunks(
            "cats", chunks, chunk_embeddings, threshold=0.8
        )
        
        assert len(results) == 0
    
    @patch.object(EmbeddingRetriever, 'get_embedding')
    def test_find_similar_chunks_top_k_limit(self, mock_get_embedding):
        """Test top_k limiting in similar chunk finding."""
        chunks = [
            TranscriptChunk(f"Text {i}", i*10, (i+1)*10, i) 
            for i in range(5)
        ]
        
        query_embedding = np.array([1, 0, 0])
        # All embeddings have decent similarity
        chunk_embeddings = [np.array([0.8, 0.2, 0]) for _ in range(5)]
        
        mock_get_embedding.return_value = query_embedding
        
        results = self.retriever.find_similar_chunks(
            "query", chunks, chunk_embeddings, top_k=3, threshold=0.1
        )
        
        assert len(results) == 3
    
    def test_prepare_context_basic(self):
        """Test basic context preparation."""
        chunks_with_scores = [
            (TranscriptChunk("First chunk", 0, 10, 0), 0.9),
            (TranscriptChunk("Second chunk", 10, 20, 1), 0.8)
        ]
        
        context = self.retriever.prepare_context(chunks_with_scores)
        
        assert "First chunk" in context
        assert "Second chunk" in context
        assert "[00:00–00:10]" in context
        assert "[00:10–00:20]" in context
    
    def test_prepare_context_max_length(self):
        """Test context preparation with length limit."""
        long_text = "A" * 1000
        chunks_with_scores = [
            (TranscriptChunk(long_text, 0, 10, 0), 0.9),
            (TranscriptChunk("Second chunk", 10, 20, 1), 0.8)
        ]
        
        context = self.retriever.prepare_context(chunks_with_scores, max_length=500)
        
        assert len(context) <= 500
        assert long_text[:400] in context  # Should include first chunk
    
    def test_prepare_context_empty(self):
        """Test context preparation with empty input."""
        context = self.retriever.prepare_context([])
        assert context == ""
    
    def test_clear_cache(self):
        """Test cache clearing."""
        # Add something to cache
        self.retriever.embeddings_cache["test"] = np.array([1, 2, 3])
        assert len(self.retriever.embeddings_cache) > 0
        
        # Clear cache
        self.retriever.clear_cache()
        assert len(self.retriever.embeddings_cache) == 0
    
    def test_mismatched_chunks_and_embeddings(self):
        """Test error handling for mismatched chunks and embeddings."""
        chunks = [TranscriptChunk("Test", 0, 10, 0)]
        embeddings = [np.array([1, 0, 0]), np.array([0, 1, 0])]  # More embeddings than chunks
        
        with patch.object(self.retriever, 'get_embedding', return_value=np.array([1, 0, 0])):
            with pytest.raises(ValueError, match="Number of chunks and embeddings must match"):
                self.retriever.find_similar_chunks("query", chunks, embeddings)
    
    @patch.object(EmbeddingRetriever, 'rate_limit_retry')
    def test_get_embedding_caching(self, mock_retry):
        """Test that embeddings are cached properly."""
        mock_retry.return_value = np.array([1, 2, 3])
        
        # First call should hit the API
        embedding1 = self.retriever.get_embedding("test text")
        assert mock_retry.call_count == 1
        
        # Second call should use cache
        embedding2 = self.retriever.get_embedding("test text")
        assert mock_retry.call_count == 1  # No additional API call
        
        # Results should be identical
        np.testing.assert_array_equal(embedding1, embedding2)
    
    @patch.object(EmbeddingRetriever, 'get_embedding')
    def test_get_embeddings_batch(self, mock_get_embedding):
        """Test batch embedding generation."""
        mock_get_embedding.side_effect = [
            np.array([1, 0, 0]),
            np.array([0, 1, 0]),
            np.array([0, 0, 1])
        ]
        
        texts = ["text1", "text2", "text3"]
        embeddings = self.retriever.get_embeddings_batch(texts)
        
        assert len(embeddings) == 3
        assert mock_get_embedding.call_count == 3
        
        # Check that each embedding is correct
        np.testing.assert_array_equal(embeddings[0], np.array([1, 0, 0]))
        np.testing.assert_array_equal(embeddings[1], np.array([0, 1, 0]))
        np.testing.assert_array_equal(embeddings[2], np.array([0, 0, 1]))
