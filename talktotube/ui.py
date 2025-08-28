"""Streamlit UI components for TalkToTube."""

import streamlit as st
import logging
from typing import List, Tuple, Optional, Dict, Any

from .config import Config
from .pipeline import TalkToTubePipeline, ProcessingResult

logger = logging.getLogger(__name__)


class TalkToTubeUI:
    """Streamlit UI manager for TalkToTube."""
    
    def __init__(self):
        """Initialize the UI manager."""
        self.pipeline = TalkToTubePipeline()
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title="TalkToTube - AI YouTube Chat",
            page_icon="🎥",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        if 'processing_result' not in st.session_state:
            st.session_state.processing_result = None
        
        if 'qa_history' not in st.session_state:
            st.session_state.qa_history = []
        
        if 'current_url' not in st.session_state:
            st.session_state.current_url = ""
        
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = "ready"
    
    def render_header(self) -> None:
        """Render the application header."""
        st.title("🎥 TalkToTube")
        st.markdown("**AI-powered YouTube video analysis and Q&A**")
        st.markdown("---")
    
    def render_sidebar(self) -> Dict[str, Any]:
        """
        Render the sidebar with configuration options.
        
        Returns:
            Dictionary of configuration values
        """
        st.sidebar.header("⚙️ Configuration")
        
        # Model settings
        st.sidebar.subheader("Models")
        st.sidebar.text(f"Whisper: {Config.WHISPER_MODEL}")
        st.sidebar.text(f"Summarization: {Config.SUMMARIZATION_MODEL}")
        st.sidebar.text(f"Q&A: {Config.QA_MODEL}")
        st.sidebar.text(f"Embeddings: {Config.EMBEDDING_MODEL}")
        
        st.sidebar.markdown("---")
        
        # Processing settings
        st.sidebar.subheader("Processing Settings")
        
        similarity_threshold = st.sidebar.slider(
            "Similarity Threshold",
            min_value=0.1,
            max_value=0.8,
            value=Config.SIMILARITY_THRESHOLD,
            step=0.05,
            help="Minimum similarity score for Q&A retrieval"
        )
        
        top_k = st.sidebar.slider(
            "Top K Chunks",
            min_value=1,
            max_value=10,
            value=Config.TOP_K_CHUNKS,
            step=1,
            help="Number of chunks to retrieve for Q&A"
        )
        
        max_duration = st.sidebar.slider(
            "Max Video Duration (minutes)",
            min_value=5,
            max_value=120,
            value=60,
            step=5,
            help="Maximum duration for audio transcription fallback"
        )
        
        st.sidebar.markdown("---")
        
        # Translation option
        translate_to_english = st.sidebar.checkbox(
            "Translate to English",
            value=False,
            help="Translate non-English content to English"
        )
        
        st.sidebar.markdown("---")

        # Video requirements info
        st.sidebar.subheader("📋 Video Requirements")
        st.sidebar.markdown("""
        **✅ Supported:**
        - Public YouTube videos
        - Videos with captions/transcripts
        - Educational content
        - Tutorials and talks

        **❌ Not Supported:**
        - Private/unlisted videos
        - Age-restricted content
        - Videos requiring sign-in
        - Live streams
        """)

        st.sidebar.markdown("---")

        # Clear session button
        if st.sidebar.button("🗑️ Clear Session"):
            self.clear_session()
            st.rerun()
        
        return {
            'similarity_threshold': similarity_threshold,
            'top_k': top_k,
            'max_duration': max_duration * 60,  # Convert to seconds
            'translate_to_english': translate_to_english
        }
    
    def render_url_input(self) -> Optional[str]:
        """
        Render URL input section.
        
        Returns:
            YouTube URL if provided
        """
        st.header("📺 YouTube Video")
        
        url = st.text_input(
            "Enter YouTube URL:",
            value=st.session_state.current_url,
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any public YouTube video URL here"
        )

        # Add demo and example URLs
        st.markdown("**💡 Try these options:**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🎯 Demo Mode", help="Use demo data to test all features", type="primary"):
                st.session_state.current_url = "https://www.youtube.com/watch?v=demo_ml_intro"
                st.rerun()

        with col2:
            if st.button("🎓 Educational", help="Khan Academy - What is Machine Learning?"):
                st.session_state.current_url = "https://www.youtube.com/watch?v=ukzFI9rgwfU"
                st.rerun()

        with col3:
            if st.button("🔬 Science", help="Crash Course - DNA Structure"):
                st.session_state.current_url = "https://www.youtube.com/watch?v=8kK2zwjRV0M"
                st.rerun()

        with col4:
            if st.button("💻 Tech", help="Python Tutorial - Variables"):
                st.session_state.current_url = "https://www.youtube.com/watch?v=Z1Yd7upQsXY"
                st.rerun()

        if st.session_state.current_url and 'demo' in st.session_state.current_url:
            st.info("🎯 **Demo Mode**: Using sample data to demonstrate all TalkToTube features without YouTube API dependencies.")
        
        col1, col2 = st.columns([1, 4])

        with col1:
            process_button = st.button("🚀 Process Video", type="primary")

        with col2:
            if st.session_state.processing_result:
                st.success(f"✅ Processed: {st.session_state.processing_result.video_info.get('title', 'Video')}")

        # Validate URL format
        if process_button and url:
            if not url.strip():
                st.error("Please enter a YouTube URL")
                return None
            elif 'youtube.com' not in url and 'youtu.be' not in url:
                st.error("Please enter a valid YouTube URL")
                return None
            else:
                return url

        return None
    
    def render_processing_status(self, status: str, message: str = "") -> None:
        """
        Render processing status indicators.
        
        Args:
            status: Current processing status
            message: Status message
        """
        status_container = st.container()
        
        with status_container:
            if status == "fetching":
                st.info("🔍 Fetching transcript...")
            elif status == "transcribing":
                st.info("🎤 Transcribing audio...")
            elif status == "normalizing":
                st.info("📝 Normalizing transcript...")
            elif status == "chunking":
                st.info("✂️ Chunking transcript...")
            elif status == "summarizing":
                st.info("📋 Generating summary...")
            elif status == "indexing":
                st.info("🔍 Indexing for Q&A...")
            elif status == "complete":
                st.success("✅ Processing complete!")
            elif status == "error":
                st.error(f"❌ Error: {message}")
    
    def process_video_with_status(self, url: str, config: Dict[str, Any]) -> None:
        """
        Process video with status updates.

        Args:
            url: YouTube URL
            config: Configuration dictionary
        """
        try:
            # Quick check first
            st.session_state.processing_status = "checking"
            st.info("🔍 Checking video accessibility...")

            from .agents.fetch_transcript import TranscriptFetcher
            fetcher = TranscriptFetcher()
            is_accessible, error_msg = fetcher.quick_video_check(url)

            if not is_accessible:
                raise ValueError(error_msg)

            st.session_state.processing_status = "fetching"
            self.render_processing_status("fetching")

            # Process the video
            result = self.pipeline.process_video(url, config['max_duration'])
            
            # Handle translation if requested
            if config['translate_to_english'] and result.language != 'en':
                st.session_state.processing_status = "translating"
                st.info("🌐 Translating to English...")
                
                # Translate summary
                translated_summary = self.pipeline.translate_content(result.summary)
                result.summary = translated_summary
                
                # Translate bullet points
                translated_bullets = []
                for bullet in result.bullet_points:
                    translated_bullet = self.pipeline.translate_content(bullet)
                    translated_bullets.append(translated_bullet)
                result.bullet_points = translated_bullets
            
            # Store results
            st.session_state.processing_result = result
            st.session_state.current_url = url
            st.session_state.qa_history = []
            st.session_state.processing_status = "complete"
            
            self.render_processing_status("complete")
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            st.session_state.processing_status = "error"

            # Provide user-friendly error messages
            error_msg = str(e)
            if 'sign in' in error_msg.lower() or 'bot' in error_msg.lower():
                friendly_msg = "⚠️ This video requires sign-in or has bot protection. Please try a different public video."
            elif 'private' in error_msg.lower() or 'unavailable' in error_msg.lower():
                friendly_msg = "⚠️ This video is private or unavailable. Please try a different public video."
            elif 'age' in error_msg.lower():
                friendly_msg = "⚠️ This video is age-restricted. Please try a different video."
            elif 'transcript' in error_msg.lower() and 'disabled' in error_msg.lower():
                friendly_msg = "⚠️ Transcripts are disabled for this video. Please try a different video."
            elif 'too long' in error_msg.lower():
                friendly_msg = f"⚠️ {error_msg} Please try a shorter video or increase the duration limit in settings."
            else:
                friendly_msg = f"❌ {error_msg}"

            self.render_processing_status("error", friendly_msg)
    
    def render_video_info(self, result: ProcessingResult) -> None:
        """
        Render video information section.
        
        Args:
            result: Processing result
        """
        st.header("📊 Video Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Title", result.video_info.get('title', 'Unknown'))
        
        with col2:
            st.metric("Channel", result.video_info.get('channel', 'Unknown'))
        
        with col3:
            st.metric("Method", result.processing_method.replace('_', ' ').title())
        
        # Additional info
        if result.video_info.get('url'):
            st.markdown(f"**URL:** {result.video_info['url']}")
        
        st.markdown(f"**Language:** {result.language}")
        st.markdown(f"**Chunks:** {len(result.chunks)}")
    
    def render_summary(self, result: ProcessingResult) -> None:
        """
        Render summary section.
        
        Args:
            result: Processing result
        """
        st.header("📋 Summary")
        
        if result.bullet_points:
            for bullet in result.bullet_points:
                st.markdown(bullet)
        else:
            st.markdown(result.summary)
    
    def render_transcript_preview(self, result: ProcessingResult) -> None:
        """
        Render transcript preview section.
        
        Args:
            result: Processing result
        """
        st.header("📜 Transcript Preview")
        
        preview = self.pipeline.get_transcript_preview(result.transcript_text)
        
        with st.expander("View Transcript", expanded=False):
            st.text(preview)
    
    def render_qa_section(self, config: Dict[str, Any]) -> None:
        """
        Render Q&A section.
        
        Args:
            config: Configuration dictionary
        """
        st.header("💬 Ask Questions")
        
        # Display Q&A history
        if st.session_state.qa_history:
            st.subheader("Previous Questions")
            for i, (question, answer) in enumerate(st.session_state.qa_history):
                with st.expander(f"Q{i+1}: {question}", expanded=False):
                    st.markdown(f"**A:** {answer}")
        
        # New question input
        question = st.text_input(
            "Ask a question about the video:",
            placeholder="What is the main topic discussed?",
            key="question_input"
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            ask_button = st.button("❓ Ask", type="primary")
        
        if ask_button and question:
            with st.spinner("🤔 Thinking..."):
                answer, citations = self.pipeline.answer_question(
                    question,
                    config['similarity_threshold'],
                    config['top_k']
                )
            
            # Display answer
            st.markdown(f"**Q:** {question}")
            st.markdown(f"**A:** {answer}")
            
            # Store in history
            st.session_state.qa_history.append((question, answer))
            
            # Clear input
            st.session_state.question_input = ""
            st.rerun()
    
    def render_export_section(self) -> None:
        """Render export section."""
        st.header("📤 Export")
        
        if st.button("📋 Copy as Markdown"):
            result = st.session_state.processing_result
            markdown_content = self.pipeline.export_to_markdown(
                result, 
                st.session_state.qa_history
            )
            
            # Display markdown in a text area for copying
            st.text_area(
                "Markdown Content (Copy this):",
                value=markdown_content,
                height=300,
                help="Copy this content to save your analysis"
            )
    
    def clear_session(self) -> None:
        """Clear current session."""
        st.session_state.processing_result = None
        st.session_state.qa_history = []
        st.session_state.current_url = ""
        st.session_state.processing_status = "ready"
        self.pipeline.clear_session()
        st.success("Session cleared!")
    
    def run(self) -> None:
        """Run the main Streamlit application."""
        self.render_header()
        
        # Sidebar configuration
        config = self.render_sidebar()
        
        # Main content
        url = self.render_url_input()
        
        # Process video if URL provided
        if url and url != st.session_state.current_url:
            self.process_video_with_status(url, config)
        
        # Display results if available
        if st.session_state.processing_result:
            result = st.session_state.processing_result
            
            self.render_video_info(result)
            st.markdown("---")
            
            self.render_summary(result)
            st.markdown("---")
            
            self.render_qa_section(config)
            st.markdown("---")
            
            self.render_transcript_preview(result)
            st.markdown("---")
            
            self.render_export_section()
        
        # Footer
        st.markdown("---")
        st.markdown("*Powered by AI • Built with Python & Streamlit*")
