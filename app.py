"""
TalkToTube - AI-powered YouTube video analysis and Q&A

A Streamlit application that processes YouTube videos to provide:
- Automatic transcript fetching or audio transcription
- AI-powered summarization
- Interactive Q&A with citations
- Markdown export functionality

Usage:
    streamlit run app.py
"""

import streamlit as st
import logging
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from talktotube.config import Config, setup_logging, validate_config
from talktotube.ui import TalkToTubeUI

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def main() -> None:
    """Main application entry point."""
    try:
        # Validate configuration
        validate_config()
        
        # Initialize and run the UI
        app = TalkToTubeUI()
        app.run()
        
    except ValueError as e:
        # Configuration error
        st.error("⚠️ Configuration Error")
        st.error(str(e))
        
        st.markdown("### Setup Instructions:")
        st.markdown("1. Get a HuggingFace API token from https://huggingface.co/settings/tokens")
        st.markdown("2. Create a `.env` file in the project root")
        st.markdown("3. Add your token: `HUGGINGFACEHUB_API_TOKEN=your_token_here`")
        st.markdown("4. Restart the application")
        
        st.stop()
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Application error: {e}")
        st.error("❌ An unexpected error occurred")
        st.error(str(e))
        
        if Config.DEBUG:
            st.exception(e)


if __name__ == "__main__":
    main()
