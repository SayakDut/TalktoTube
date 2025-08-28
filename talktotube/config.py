"""Configuration management for TalkToTube."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Configuration
    HUGGINGFACE_API_TOKEN: Optional[str] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    
    # Debug Configuration
    DEBUG: bool = os.getenv("TALKTOTUBE_DEBUG", "false").lower() == "true"

    # Offline mode for testing without API calls
    OFFLINE_MODE: bool = os.getenv("TALKTOTUBE_OFFLINE", "false").lower() == "true"
    
    # Model Configuration
    WHISPER_MODEL: str = "openai/whisper-small"
    SUMMARIZATION_MODEL: str = "facebook/bart-large-cnn"
    QA_MODEL: str = "google/flan-t5-base"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Processing Configuration
    CHUNK_SIZE_TOKENS: int = 1000
    CHUNK_SIZE_WORDS_FALLBACK: int = 1200
    CHUNK_OVERLAP_PERCENT: float = 0.125  # 12.5%
    
    # Retrieval Configuration
    SIMILARITY_THRESHOLD: float = 0.35
    TOP_K_CHUNKS: int = 5
    
    # API Configuration
    HF_TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_SECONDS: list[int] = [1, 2, 4]
    
    # Text Processing
    MAX_CONTEXT_LENGTH: int = 2000  # Safe limit for most models
    SUMMARY_PROMPT: str = (
        "Summarize the following transcript into 5–8 key bullet points. "
        "Include timestamps if present. Keep it concise and factual."
    )
    
    QA_PROMPT_TEMPLATE: str = (
        "Answer the following question using ONLY the provided context. "
        "If the context does not contain the answer, reply 'Not found in video.' "
        "Context: {context} "
        "Question: {question} "
        "Answer:"
    )


def setup_logging() -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if Config.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)


def validate_config() -> None:
    """Validate required configuration."""
    if not Config.HUGGINGFACE_API_TOKEN:
        raise ValueError(
            "HUGGINGFACEHUB_API_TOKEN environment variable is required. "
            "Please set it in your .env file or environment."
        )


# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Validate configuration on import
try:
    validate_config()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    # Don't raise here to allow imports during development
