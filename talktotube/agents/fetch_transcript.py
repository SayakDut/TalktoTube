"""Agent for fetching YouTube transcripts using youtube-transcript-api."""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable,
    TooManyRequests
)

logger = logging.getLogger(__name__)


class TranscriptFetcher:
    """Handles fetching transcripts from YouTube videos."""
    
    def __init__(self):
        """Initialize the transcript fetcher."""
        pass
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID if found, None otherwise
        """
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.debug(f"Extracted video ID: {video_id}")
                return video_id
        
        # Try parsing as URL
        try:
            parsed = urlparse(url)
            if 'youtube.com' in parsed.netloc:
                query_params = parse_qs(parsed.query)
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    logger.debug(f"Extracted video ID from query params: {video_id}")
                    return video_id
            elif 'youtu.be' in parsed.netloc:
                video_id = parsed.path.lstrip('/')
                if len(video_id) == 11:
                    logger.debug(f"Extracted video ID from youtu.be: {video_id}")
                    return video_id
        except Exception as e:
            logger.warning(f"Failed to parse URL: {e}")
        
        logger.error(f"Could not extract video ID from URL: {url}")
        return None
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        Get basic video information (placeholder for future enhancement).
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video metadata
        """
        # For now, return basic info
        # In a full implementation, you might use yt-dlp or YouTube API
        return {
            'video_id': video_id,
            'title': 'Unknown Title',
            'channel': 'Unknown Channel',
            'duration': 'Unknown Duration',
            'url': f'https://www.youtube.com/watch?v={video_id}'
        }
    
    def fetch_transcript(self, url: str, language_codes: List[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Fetch transcript for a YouTube video.
        
        Args:
            url: YouTube video URL
            language_codes: Preferred language codes (e.g., ['en', 'en-US'])
            
        Returns:
            Tuple of (transcript_data, video_info)
            
        Raises:
            ValueError: If video ID cannot be extracted
            TranscriptsDisabled: If transcripts are disabled for the video
            NoTranscriptFound: If no transcript is available
            VideoUnavailable: If video is not accessible
        """
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            raise ValueError(f"Could not extract video ID from URL: {url}")
        
        # Get video info
        video_info = self.get_video_info(video_id)
        
        # Set default language preferences
        if language_codes is None:
            language_codes = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
        
        try:
            logger.info(f"Fetching transcript for video: {video_id}")

            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # First, try to find manually created transcripts
            for lang_code in language_codes:
                try:
                    transcript = transcript_list.find_manually_created_transcript([lang_code])
                    transcript_data = transcript.fetch()
                    logger.info(f"Found manually created transcript in {lang_code}")
                    return transcript_data, video_info
                except (NoTranscriptFound, Exception):
                    continue

            # If no manual transcripts, try auto-generated
            for lang_code in language_codes:
                try:
                    transcript = transcript_list.find_generated_transcript([lang_code])
                    transcript_data = transcript.fetch()
                    logger.info(f"Found auto-generated transcript in {lang_code}")
                    return transcript_data, video_info
                except (NoTranscriptFound, Exception):
                    continue
            
            # If no transcripts in preferred languages, try any available
            try:
                # Get any available transcript
                available_transcripts = list(transcript_list)
                if available_transcripts:
                    transcript = available_transcripts[0]
                    transcript_data = transcript.fetch()
                    logger.info(f"Found transcript in {transcript.language_code}")
                    
                    # Try to translate to English if not English
                    if transcript.language_code not in ['en', 'en-US', 'en-GB']:
                        try:
                            translated = transcript.translate('en')
                            transcript_data = translated.fetch()
                            logger.info(f"Translated transcript from {transcript.language_code} to English")
                        except Exception as e:
                            logger.warning(f"Failed to translate transcript: {e}")
                    
                    return transcript_data, video_info
                else:
                    raise NoTranscriptFound(video_id, [], None)
                    
            except Exception as e:
                logger.error(f"Failed to fetch any transcript: {e}")
                raise
                
        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video: {video_id}")
            raise
        except NoTranscriptFound:
            logger.error(f"No transcript found for video: {video_id}")
            raise
        except VideoUnavailable:
            logger.error(f"Video is unavailable: {video_id}")
            raise
        except TooManyRequests:
            logger.error("Too many requests to YouTube API")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching transcript: {e}")
            raise
    
    def is_transcript_available(self, url: str) -> bool:
        """
        Check if transcript is available for a video without fetching it.

        Args:
            url: YouTube video URL

        Returns:
            True if transcript is likely available
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return False

            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_transcripts = list(transcript_list)
            return len(available_transcripts) > 0

        except Exception:
            return False

    def quick_video_check(self, url: str) -> tuple[bool, str]:
        """
        Quick check if video is accessible and has basic info.

        Args:
            url: YouTube video URL

        Returns:
            Tuple of (is_accessible, error_message)
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                return False, "Invalid YouTube URL"

            # Try to get basic video info first
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                return True, "Video accessible"
            except VideoUnavailable:
                return False, "Video is unavailable or private"
            except TranscriptsDisabled:
                return False, "Transcripts are disabled for this video"
            except TooManyRequests:
                return False, "Too many requests - please try again later"
            except Exception as e:
                error_msg = str(e).lower()
                if 'sign in' in error_msg or 'bot' in error_msg:
                    return False, "Video requires sign-in or has bot protection"
                return False, f"Video access error: {str(e)}"

        except Exception as e:
            return False, f"URL processing error: {str(e)}"
