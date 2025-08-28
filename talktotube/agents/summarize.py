"""Summarization agent using BART via HuggingFace Inference API."""

import logging
import time
from typing import List, Dict, Any
from huggingface_hub import InferenceClient

from ..config import Config
from ..utils.text import TranscriptChunk

logger = logging.getLogger(__name__)


class SummarizationAgent:
    """Handles text summarization using BART model."""
    
    def __init__(self):
        """Initialize the summarization agent."""
        self.client = InferenceClient(token=Config.HUGGINGFACE_API_TOKEN)
    
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
    
    def prepare_text_for_summarization(self, transcript_text: str, max_length: int = 4000) -> str:
        """
        Prepare transcript text for summarization by truncating if necessary.
        
        Args:
            transcript_text: Full transcript text
            max_length: Maximum length in characters
            
        Returns:
            Prepared text for summarization
        """
        if len(transcript_text) <= max_length:
            return transcript_text
        
        # Truncate at sentence boundary if possible
        truncated = transcript_text[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        # Find the last sentence ending
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.8:  # If we can keep at least 80% of content
            truncated = truncated[:last_sentence_end + 1]
        
        logger.info(f"Truncated transcript from {len(transcript_text)} to {len(truncated)} characters")
        return truncated
    
    def summarize_text(self, text: str, custom_prompt: str = None) -> str:
        """
        Summarize text using BART model.
        
        Args:
            text: Text to summarize
            custom_prompt: Custom prompt for summarization
            
        Returns:
            Summary text
            
        Raises:
            Exception: If summarization fails
        """
        if not text.strip():
            return "No content to summarize."
        
        # Prepare text
        prepared_text = self.prepare_text_for_summarization(text)
        
        # Use custom prompt or default
        prompt = custom_prompt or Config.SUMMARY_PROMPT
        
        # Combine prompt with text
        full_input = f"{prompt}\n\nTranscript:\n{prepared_text}"
        
        def _summarize():
            response = self.client.text_generation(
                prompt=full_input,
                model=Config.SUMMARIZATION_MODEL,
                max_new_tokens=500,
                temperature=0.3,
                do_sample=True,
                return_full_text=False
            )
            return response
        
        try:
            logger.info(f"Summarizing text ({len(prepared_text)} characters)")

            # Check if offline mode is enabled
            if Config.OFFLINE_MODE:
                logger.info("Offline mode: generating mock summary")
                result = self.generate_offline_summary(prepared_text)
            else:
                # Call BART API with retry
                result = self.rate_limit_retry(_summarize)
            
            # Extract summary from response - handle multiple formats
            summary = "Failed to generate summary."

            try:
                if isinstance(result, str):
                    summary = result.strip()
                elif isinstance(result, dict):
                    if 'generated_text' in result:
                        summary = result['generated_text'].strip()
                    elif 'text' in result:
                        summary = result['text'].strip()
                    elif len(result) == 1:
                        # Single key-value pair
                        summary = str(list(result.values())[0]).strip()
                    else:
                        summary = str(result).strip()
                elif isinstance(result, list) and len(result) > 0:
                    first_item = result[0]
                    if isinstance(first_item, dict):
                        if 'generated_text' in first_item:
                            summary = first_item['generated_text'].strip()
                        elif 'text' in first_item:
                            summary = first_item['text'].strip()
                        else:
                            summary = str(first_item).strip()
                    else:
                        summary = str(first_item).strip()
                else:
                    logger.warning(f"Unexpected summarization response format: {type(result)} - {result}")
                    summary = "Could not parse summary from API response."
            except Exception as parse_error:
                logger.error(f"Error parsing summary response: {parse_error}")
                summary = "Error parsing summary response."
            
            # Clean up summary
            summary = self.clean_summary(summary)
            
            logger.info(f"Generated summary ({len(summary)} characters)")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to summarize text: {e}")
            raise

    def generate_offline_summary(self, text: str) -> str:
        """
        Generate a mock summary for offline mode.

        Args:
            text: Input text

        Returns:
            Mock summary
        """
        # Simple offline summary based on text analysis
        lines = text.split('\n')
        key_points = []

        for line in lines:
            if line.strip() and len(line.strip()) > 20:
                # Extract first sentence or meaningful chunk
                sentences = line.split('.')
                if sentences and len(sentences[0].strip()) > 10:
                    key_points.append(f"• {sentences[0].strip()}")
                    if len(key_points) >= 6:
                        break

        if not key_points:
            key_points = [
                "• This video covers machine learning fundamentals",
                "• Explains supervised, unsupervised, and reinforcement learning",
                "• Discusses popular algorithms and applications",
                "• Provides guidance on getting started with ML",
                "• Covers data preprocessing and model evaluation"
            ]

        return '\n'.join(key_points[:6])

    def clean_summary(self, summary: str) -> str:
        """
        Clean and format the generated summary.
        
        Args:
            summary: Raw summary text
            
        Returns:
            Cleaned summary
        """
        if not summary:
            return "No summary generated."
        
        # Remove any prompt repetition
        lines = summary.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that look like prompt repetition
            if any(phrase in line.lower() for phrase in [
                'summarize the following',
                'transcript:',
                'key bullet points',
                'include timestamps'
            ]):
                continue
            
            cleaned_lines.append(line)
        
        # Join lines and ensure bullet point format
        summary = '\n'.join(cleaned_lines)
        
        # Ensure bullet points
        if summary and not any(line.strip().startswith(('•', '-', '*', '1.', '2.')) for line in summary.split('\n')):
            # Convert to bullet points if not already formatted
            sentences = [s.strip() for s in summary.split('.') if s.strip()]
            if len(sentences) > 1:
                summary = '\n'.join(f"• {sentence}." for sentence in sentences[:8])
        
        return summary
    
    def summarize_chunks(self, chunks: List[TranscriptChunk]) -> str:
        """
        Summarize transcript chunks with timestamp preservation.
        
        Args:
            chunks: List of transcript chunks
            
        Returns:
            Summary with timestamps
        """
        if not chunks:
            return "No content to summarize."
        
        # Combine chunks into text with timestamps
        text_parts = []
        for chunk in chunks:
            timestamp = chunk.get_citation()
            text_parts.append(f"{timestamp} {chunk.text}")
        
        combined_text = '\n'.join(text_parts)
        
        # Create custom prompt that emphasizes timestamps
        custom_prompt = (
            "Summarize the following timestamped transcript into 5–8 key bullet points. "
            "Include relevant timestamps in your summary. Keep it concise and factual. "
            "Format each point as a bullet point."
        )
        
        return self.summarize_text(combined_text, custom_prompt)
    
    def create_bullet_summary(self, transcript_text: str) -> List[str]:
        """
        Create a bullet-point summary from transcript.
        
        Args:
            transcript_text: Full transcript text
            
        Returns:
            List of bullet points
        """
        summary = self.summarize_text(transcript_text)
        
        # Split into bullet points
        lines = summary.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Clean up bullet point formatting
            if line.startswith(('•', '-', '*')):
                bullet_points.append(line)
            elif line[0].isdigit() and '.' in line[:3]:
                # Convert numbered list to bullets
                bullet_points.append('• ' + line.split('.', 1)[1].strip())
            elif line and not any(line.startswith(bp[:10]) for bp in bullet_points):
                # Add bullet if not already present and not duplicate
                bullet_points.append('• ' + line)
        
        # Limit to reasonable number of points
        return bullet_points[:8]
