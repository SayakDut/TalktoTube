"""Q&A agent using retrieval-augmented generation with FLAN-T5."""

import logging
import time
from typing import List, Dict, Any, Tuple, Optional
from huggingface_hub import InferenceClient

from ..config import Config
from ..utils.text import TranscriptChunk
from ..utils.retrieval import EmbeddingRetriever

logger = logging.getLogger(__name__)


class QAAgent:
    """Handles question answering using retrieval-augmented generation."""
    
    def __init__(self):
        """Initialize the Q&A agent."""
        self.client = InferenceClient(token=Config.HUGGINGFACE_API_TOKEN)
        self.retriever = EmbeddingRetriever()
        self.chunks: List[TranscriptChunk] = []
        self.chunk_embeddings: List[Any] = []
    
    def rate_limit_retry(self, func, *args, **kwargs) -> Any:
        """Execute function with exponential backoff retry."""
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
    
    def index_chunks(self, chunks: List[TranscriptChunk]) -> None:
        """
        Index transcript chunks for retrieval.
        
        Args:
            chunks: List of transcript chunks to index
        """
        if not chunks:
            logger.warning("No chunks to index")
            return
        
        logger.info(f"Indexing {len(chunks)} chunks for retrieval")
        
        # Store chunks
        self.chunks = chunks
        
        # Generate embeddings for all chunks
        chunk_texts = [chunk.text for chunk in chunks]
        self.chunk_embeddings = self.retriever.get_embeddings_batch(chunk_texts)
        
        logger.info(f"Successfully indexed {len(self.chunk_embeddings)} chunk embeddings")
    
    def generate_answer(self, question: str, context: str) -> str:
        """
        Generate answer using FLAN-T5 model.
        
        Args:
            question: User question
            context: Retrieved context
            
        Returns:
            Generated answer
        """
        # Format prompt using template
        prompt = Config.QA_PROMPT_TEMPLATE.format(
            context=context,
            question=question
        )
        
        # Ensure prompt doesn't exceed model limits
        if len(prompt) > Config.MAX_CONTEXT_LENGTH:
            # Truncate context while preserving question
            available_length = Config.MAX_CONTEXT_LENGTH - len(question) - 200  # Buffer for template
            truncated_context = context[:available_length]
            prompt = Config.QA_PROMPT_TEMPLATE.format(
                context=truncated_context,
                question=question
            )
        
        def _generate():
            response = self.client.text_generation(
                prompt=prompt,
                model=Config.QA_MODEL,
                max_new_tokens=200,
                temperature=0.1,
                do_sample=True,
                return_full_text=False
            )
            return response
        
        try:
            logger.debug(f"Generating answer for question: {question[:50]}...")

            # Check if offline mode is enabled
            if Config.OFFLINE_MODE:
                logger.info("Offline mode: generating mock answer")
                result = self.generate_offline_answer(question, context)
            else:
                # Call FLAN-T5 API with retry
                result = self.rate_limit_retry(_generate)
            
            # Extract answer from response - handle multiple formats
            answer = "I couldn't generate an answer."

            try:
                if isinstance(result, str):
                    answer = result.strip()
                elif isinstance(result, dict):
                    if 'generated_text' in result:
                        answer = result['generated_text'].strip()
                    elif 'text' in result:
                        answer = result['text'].strip()
                    elif len(result) == 1:
                        # Single key-value pair
                        answer = str(list(result.values())[0]).strip()
                    else:
                        answer = str(result).strip()
                elif isinstance(result, list) and len(result) > 0:
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        if 'generated_text' in first_item:
                            answer = first_item['generated_text'].strip()
                        elif 'text' in first_item:
                            answer = first_item['text'].strip()
                        else:
                            answer = str(first_item).strip()
                    else:
                        answer = str(first_item).strip()
                else:
                    logger.warning(f"Unexpected QA response format: {type(result)} - {result}")
                    answer = "Could not parse answer from API response."
            except Exception as parse_error:
                logger.error(f"Error parsing QA response: {parse_error}")
                answer = "Error parsing answer response."
            
            # Clean up answer
            answer = self.clean_answer(answer)
            
            logger.debug(f"Generated answer: {answer[:100]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return "I encountered an error while generating the answer."
    
    def clean_answer(self, answer: str) -> str:
        """
        Clean and format the generated answer.
        
        Args:
            answer: Raw answer text
            
        Returns:
            Cleaned answer
        """
        if not answer:
            return "I couldn't find an answer."
        
        # Remove common artifacts
        answer = answer.strip()
        
        # Remove prompt repetition
        if answer.lower().startswith('answer:'):
            answer = answer[7:].strip()
        
        # Handle common model responses
        if answer.lower() in ['', 'none', 'n/a', 'not applicable']:
            return "Not found in video."
        
        # Ensure proper capitalization
        if answer and answer[0].islower():
            answer = answer[0].upper() + answer[1:]
        
        return answer

    def generate_offline_answer(self, question: str, context: str) -> str:
        """
        Generate a mock answer for offline mode.

        Args:
            question: User question
            context: Retrieved context

        Returns:
            Mock answer
        """
        question_lower = question.lower()

        # Simple keyword-based responses
        if any(word in question_lower for word in ['what', 'define', 'explain']):
            if 'machine learning' in question_lower:
                return "Machine learning is a subset of artificial intelligence that enables computers to learn from data."
            elif 'supervised' in question_lower:
                return "Supervised learning uses labeled data to train models to make predictions."
            elif 'neural network' in question_lower:
                return "Neural networks are computing systems inspired by biological neural networks."
            else:
                return "This concept is explained in the video content with relevant examples."

        elif any(word in question_lower for word in ['how', 'process', 'work']):
            return "The process involves multiple steps as described in the video, including data preparation and model training."

        elif any(word in question_lower for word in ['why', 'reason', 'benefit']):
            return "This approach is beneficial because it provides accurate results and is widely applicable."

        elif any(word in question_lower for word in ['when', 'time', 'use']):
            return "This technique is typically used when you have sufficient data and clear objectives."

        else:
            return "Based on the video content, this topic is covered with practical examples and explanations."

    def answer_question(
        self, 
        question: str, 
        similarity_threshold: float = None,
        top_k: int = None
    ) -> Tuple[str, List[str]]:
        """
        Answer a question using retrieval-augmented generation.
        
        Args:
            question: User question
            similarity_threshold: Minimum similarity threshold for retrieval
            top_k: Number of top chunks to retrieve
            
        Returns:
            Tuple of (answer, citations)
        """
        if not self.chunks or not self.chunk_embeddings:
            return "No content has been indexed for Q&A.", []
        
        similarity_threshold = similarity_threshold or Config.SIMILARITY_THRESHOLD
        top_k = top_k or Config.TOP_K_CHUNKS
        
        try:
            # Retrieve relevant chunks
            similar_chunks = self.retriever.find_similar_chunks(
                query=question,
                chunks=self.chunks,
                chunk_embeddings=self.chunk_embeddings,
                top_k=top_k,
                threshold=similarity_threshold
            )
            
            if not similar_chunks:
                logger.info(f"No chunks found above threshold {similarity_threshold}")
                return "Not found in video.", []
            
            # Check if best similarity is below threshold
            best_similarity = similar_chunks[0][1]
            if best_similarity < similarity_threshold:
                logger.info(f"Best similarity {best_similarity:.3f} below threshold {similarity_threshold}")
                return "Not found in video.", []
            
            # Prepare context
            context = self.retriever.prepare_context(similar_chunks)
            
            if not context:
                return "Not found in video.", []
            
            # Generate answer
            answer = self.generate_answer(question, context)
            
            # Extract citations
            citations = [chunk.get_citation() for chunk, _ in similar_chunks]
            
            # Add citations to answer if not already present
            if answer and answer != "Not found in video." and citations:
                # Check if answer already has citations
                if not any(citation in answer for citation in citations):
                    citation_text = " " + " ".join(citations)
                    answer += citation_text
            
            logger.info(f"Answered question with {len(similar_chunks)} relevant chunks")
            return answer, citations
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return "I encountered an error while processing your question.", []
    
    def translate_to_english(self, text: str, source_language: str = "auto") -> str:
        """
        Translate text to English using the QA model (simple approach).
        
        Args:
            text: Text to translate
            source_language: Source language code
            
        Returns:
            Translated text
        """
        if not text.strip():
            return text
        
        # Simple translation prompt
        prompt = f"Translate the following text to English: {text}"
        
        try:
            def _translate():
                response = self.client.text_generation(
                    prompt=prompt,
                    model=Config.QA_MODEL,
                    max_new_tokens=len(text) + 100,
                    temperature=0.1,
                    do_sample=True,
                    return_full_text=False
                )
                return response
            
            result = self.rate_limit_retry(_translate)
            
            # Extract translation
            if isinstance(result, str):
                translation = result.strip()
            elif isinstance(result, dict) and 'generated_text' in result:
                translation = result['generated_text'].strip()
            else:
                translation = text  # Fallback to original
            
            logger.info(f"Translated text ({len(text)} -> {len(translation)} chars)")
            return translation
            
        except Exception as e:
            logger.error(f"Failed to translate text: {e}")
            return text  # Return original on failure
    
    def clear_index(self) -> None:
        """Clear the indexed chunks and embeddings."""
        self.chunks = []
        self.chunk_embeddings = []
        self.retriever.clear_cache()
        logger.info("Cleared Q&A index")
