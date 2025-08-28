"""Fallback transcription agent using yt-dlp and Whisper via HuggingFace."""

import logging
import os
import tempfile
import time
from typing import List, Dict, Any, Optional
import yt_dlp
from huggingface_hub import InferenceClient

from ..config import Config

logger = logging.getLogger(__name__)


class TranscriptionAgent:
    """Handles audio download and transcription as fallback when transcripts aren't available."""
    
    def __init__(self):
        """Initialize the transcription agent."""
        self.client = InferenceClient(token=Config.HUGGINGFACE_API_TOKEN)
        self.temp_dir = tempfile.gettempdir()
    
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
    
    def download_audio(self, url: str, max_duration: int = 3600) -> str:
        """
        Download audio from YouTube video using yt-dlp.
        
        Args:
            url: YouTube video URL
            max_duration: Maximum duration in seconds (1 hour default)
            
        Returns:
            Path to downloaded audio file
            
        Raises:
            Exception: If download fails
        """
        # Create temporary filename
        temp_audio_path = os.path.join(self.temp_dir, f"talktotube_audio_{int(time.time())}.wav")
        
        # yt-dlp options for audio extraction
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_audio_path.replace('.wav', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': not Config.DEBUG,
            'no_warnings': not Config.DEBUG,
            'extractaudio': True,
            'audioformat': 'wav',
            'match_filter': lambda info_dict: None if info_dict.get('duration', 0) <= max_duration else "Video too long",
            # Additional options to bypass restrictions
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'extractor_retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
        }
        
        try:
            logger.info(f"Downloading audio from: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract info first to check duration
                    info = ydl.extract_info(url, download=False)
                    duration = info.get('duration', 0)
                    title = info.get('title', 'Unknown')

                    logger.info(f"Video: {title}, Duration: {duration}s")

                    if duration > max_duration:
                        raise ValueError(f"Video too long: {duration}s (max: {max_duration}s)")

                    # Download the audio
                    ydl.download([url])
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'sign in' in error_msg or 'bot' in error_msg:
                        raise ValueError("This video requires sign-in or has bot protection. Please try a different video.")
                    elif 'private' in error_msg or 'unavailable' in error_msg:
                        raise ValueError("This video is private or unavailable. Please try a different video.")
                    elif 'age' in error_msg:
                        raise ValueError("This video is age-restricted. Please try a different video.")
                    else:
                        raise
            
            # Find the actual downloaded file (yt-dlp might change extension)
            base_path = temp_audio_path.replace('.wav', '')
            possible_extensions = ['.wav', '.m4a', '.mp3', '.webm']
            
            actual_path = None
            for ext in possible_extensions:
                test_path = base_path + ext
                if os.path.exists(test_path):
                    actual_path = test_path
                    break
            
            if not actual_path or not os.path.exists(actual_path):
                raise FileNotFoundError("Downloaded audio file not found")
            
            file_size = os.path.getsize(actual_path)
            logger.info(f"Audio downloaded successfully: {actual_path} ({file_size} bytes)")
            
            return actual_path
            
        except Exception as e:
            logger.error(f"Failed to download audio: {e}")
            # Clean up any partial files
            for ext in ['.wav', '.m4a', '.mp3', '.webm']:
                test_path = temp_audio_path.replace('.wav', ext)
                if os.path.exists(test_path):
                    try:
                        os.remove(test_path)
                    except:
                        pass
            raise
    
    def transcribe_audio(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Transcribe audio using Whisper via HuggingFace Inference API.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            List of transcript segments with timestamps
            
        Raises:
            Exception: If transcription fails
        """
        def _transcribe():
            with open(audio_path, 'rb') as audio_file:
                response = self.client.automatic_speech_recognition(
                    audio_file.read(),
                    model=Config.WHISPER_MODEL
                )
            return response
        
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Call Whisper API with retry
            result = self.rate_limit_retry(_transcribe)
            
            # Process Whisper response
            if isinstance(result, dict):
                # If response includes chunks with timestamps
                if 'chunks' in result:
                    segments = []
                    for chunk in result['chunks']:
                        segments.append({
                            'text': chunk.get('text', '').strip(),
                            'start': chunk.get('timestamp', [0, 0])[0],
                            'duration': chunk.get('timestamp', [0, 0])[1] - chunk.get('timestamp', [0, 0])[0]
                        })
                    return segments
                
                # If response has just text
                elif 'text' in result:
                    return [{
                        'text': result['text'].strip(),
                        'start': 0,
                        'duration': 0
                    }]
            
            # If response is just a string
            elif isinstance(result, str):
                return [{
                    'text': result.strip(),
                    'start': 0,
                    'duration': 0
                }]
            
            else:
                logger.warning(f"Unexpected Whisper response format: {type(result)}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to transcribe audio: {e}")
            raise
    
    def cleanup_audio_file(self, audio_path: str) -> None:
        """
        Clean up temporary audio file.
        
        Args:
            audio_path: Path to audio file to delete
        """
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.debug(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up audio file {audio_path}: {e}")
    
    def transcribe_from_url(self, url: str, max_duration: int = 3600) -> List[Dict[str, Any]]:
        """
        Complete pipeline: download audio and transcribe.
        
        Args:
            url: YouTube video URL
            max_duration: Maximum video duration in seconds
            
        Returns:
            List of transcript segments
            
        Raises:
            Exception: If any step fails
        """
        audio_path = None
        
        try:
            # Download audio
            audio_path = self.download_audio(url, max_duration)
            
            # Transcribe
            transcript_data = self.transcribe_audio(audio_path)
            
            logger.info(f"Successfully transcribed {len(transcript_data)} segments")
            return transcript_data
            
        finally:
            # Always clean up
            if audio_path:
                self.cleanup_audio_file(audio_path)
    
    def detect_language(self, transcript_data: List[Dict[str, Any]]) -> str:
        """
        Detect language from transcript data (placeholder).
        
        Args:
            transcript_data: Transcript segments
            
        Returns:
            Language code (defaults to 'en')
        """
        # For now, assume English
        # In a full implementation, you could use language detection
        # or check Whisper's language detection output
        return 'en'
