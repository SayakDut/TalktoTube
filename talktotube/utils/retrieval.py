"""Retrieval utilities for embedding-based similarity search."""

import logging
import time
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from huggingface_hub import InferenceClient

from ..config import Config
from .text import TranscriptChunk

logger = logging.getLogger(__name__)


class EmbeddingRetriever:
    """Handles embedding generation and similarity-based retrieval."""
    
    def __init__(self):
        """Initialize the retriever with HuggingFace client."""
        self.client = InferenceClient(token=Config.HUGGINGFACE_API_TOKEN)
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        
    def rate_limit_retry(self, func, *args, **kwargs) -> Any:
        """
        Execute function with exponential backoff retry on rate limits.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries are exhausted
        """
        last_exception = None
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < Config.MAX_RETRIES - 1:
                    wait_time = Config.RETRY_BACKOFF_SECONDS[attempt]
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All {Config.MAX_RETRIES} attempts failed")
        
        raise last_exception
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for text using HuggingFace Inference API.

        Args:
            text: Input text

        Returns:
            Embedding vector as numpy array
        """
        # Check cache first
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]

        # Check if offline mode is enabled
        if Config.OFFLINE_MODE:
            logger.debug("Offline mode: generating mock embedding")
            embedding = self.generate_mock_embedding(text)
            self.embeddings_cache[text] = embedding
            return embedding

        def _get_embedding():
            response = self.client.feature_extraction(
                text=text,
                model=Config.EMBEDDING_MODEL
            )
            return np.array(response)

        try:
            embedding = self.rate_limit_retry(_get_embedding)

            # Ensure embedding is 1D
            if embedding.ndim > 1:
                embedding = embedding.flatten()

            # Cache the result
            self.embeddings_cache[text] = embedding

            logger.debug(f"Generated embedding for text (length: {len(text)}, embedding dim: {len(embedding)})")
            return embedding

        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            # Fallback to mock embedding in case of API failure
            logger.info("Falling back to mock embedding due to API error")
            embedding = self.generate_mock_embedding(text)
            self.embeddings_cache[text] = embedding
            return embedding
    
    def get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = self.get_embedding(text)
                embeddings.append(embedding)
                
                # Small delay to avoid rate limiting
                if i < len(texts) - 1:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Failed to get embedding for text {i}: {e}")
                # Use zero vector as fallback
                embeddings.append(np.zeros(384))  # Default dimension for all-MiniLM-L6-v2
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings

    def generate_mock_embedding(self, text: str) -> np.ndarray:
        """
        Generate a mock embedding for offline mode.

        Args:
            text: Input text

        Returns:
            Mock embedding vector
        """
        # Create a deterministic but varied embedding based on text content
        import hashlib

        # Use text hash to create consistent but varied embeddings
        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Convert hash to numbers and normalize
        embedding_dim = 384  # Standard dimension for all-MiniLM-L6-v2
        embedding = np.zeros(embedding_dim)

        # Fill embedding with values based on text characteristics
        for i in range(embedding_dim):
            # Use different parts of the hash and text features
            hash_idx = i % len(text_hash)
            char_val = ord(text_hash[hash_idx]) / 255.0

            # Add some text-based features
            text_features = [
                len(text) / 1000.0,  # Text length
                text.count(' ') / len(text) if text else 0,  # Word density
                sum(1 for c in text if c.isupper()) / len(text) if text else 0,  # Uppercase ratio
            ]

            feature_val = text_features[i % len(text_features)]
            embedding[i] = (char_val + feature_val) / 2.0

        # Normalize the embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score
        """
        # Normalize vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(vec1, vec2) / (norm1 * norm2)
    
    def find_similar_chunks(
        self, 
        query: str, 
        chunks: List[TranscriptChunk], 
        chunk_embeddings: List[np.ndarray],
        top_k: int = None,
        threshold: float = None
    ) -> List[Tuple[TranscriptChunk, float]]:
        """
        Find most similar chunks to query using cosine similarity.
        
        Args:
            query: Search query
            chunks: List of transcript chunks
            chunk_embeddings: Precomputed embeddings for chunks
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (chunk, similarity_score) tuples, sorted by similarity
        """
        top_k = top_k or Config.TOP_K_CHUNKS
        threshold = threshold or Config.SIMILARITY_THRESHOLD
        
        if len(chunks) != len(chunk_embeddings):
            raise ValueError("Number of chunks and embeddings must match")
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, chunk_embedding in enumerate(chunk_embeddings):
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            similarities.append((chunks[i], similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Filter by threshold and limit to top_k
        filtered_results = [
            (chunk, score) for chunk, score in similarities 
            if score >= threshold
        ][:top_k]
        
        logger.info(f"Found {len(filtered_results)} chunks above threshold {threshold}")
        
        if filtered_results:
            max_score = filtered_results[0][1]
            logger.info(f"Best similarity score: {max_score:.3f}")
        
        return filtered_results
    
    def prepare_context(
        self,
        similar_chunks: List[Tuple[TranscriptChunk, float]],
        max_length: int = None
    ) -> str:
        """
        Prepare context text from similar chunks for Q&A.

        Args:
            similar_chunks: List of (chunk, similarity_score) tuples
            max_length: Maximum context length in characters

        Returns:
            Formatted context text with citations
        """
        max_length = max_length or Config.MAX_CONTEXT_LENGTH

        if not similar_chunks:
            return ""

        context_parts = []
        current_length = 0

        for chunk, score in similar_chunks:
            citation = chunk.get_citation()
            chunk_text = f"{chunk.text} {citation}"

            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_text) + len("\n\n") > max_length and context_parts:
                break

            # If this is the first chunk and it's too long, truncate it
            if not context_parts and len(chunk_text) > max_length:
                available_length = max_length - len(citation) - 1  # -1 for space
                truncated_text = chunk.text[:available_length]
                chunk_text = f"{truncated_text} {citation}"

            context_parts.append(chunk_text)
            current_length += len(chunk_text) + (len("\n\n") if context_parts else 0)

        context = "\n\n".join(context_parts)

        logger.debug(f"Prepared context with {len(context_parts)} chunks, {len(context)} characters")

        return context
    
    def clear_cache(self) -> None:
        """Clear the embeddings cache."""
        self.embeddings_cache.clear()
        logger.info("Cleared embeddings cache")
