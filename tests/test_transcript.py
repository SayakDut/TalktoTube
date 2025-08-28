"""Tests for transcript fetching functionality."""

import pytest
from unittest.mock import Mock, patch
from talktotube.agents.fetch_transcript import TranscriptFetcher


class TestTranscriptFetcher:
    """Test cases for TranscriptFetcher."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = TranscriptFetcher()
    
    def test_extract_video_id_standard_url(self):
        """Test video ID extraction from standard YouTube URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = self.fetcher.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test video ID extraction from short YouTube URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = self.fetcher.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test video ID extraction from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = self.fetcher.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_with_parameters(self):
        """Test video ID extraction from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s&list=PLrAXtmRdnEQy"
        video_id = self.fetcher.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test video ID extraction from invalid URL."""
        url = "https://example.com/not-youtube"
        video_id = self.fetcher.extract_video_id(url)
        assert video_id is None
    
    def test_get_video_info(self):
        """Test basic video info retrieval."""
        video_id = "dQw4w9WgXcQ"
        info = self.fetcher.get_video_info(video_id)
        
        assert isinstance(info, dict)
        assert info['video_id'] == video_id
        assert 'title' in info
        assert 'channel' in info
        assert 'duration' in info
        assert 'url' in info
    
    @patch('talktotube.agents.fetch_transcript.YouTubeTranscriptApi')
    def test_fetch_transcript_success(self, mock_api):
        """Test successful transcript fetching."""
        # Mock transcript data
        mock_transcript_data = [
            {'text': 'Hello world', 'start': 0.0, 'duration': 2.0},
            {'text': 'This is a test', 'start': 2.0, 'duration': 3.0}
        ]
        
        # Mock transcript object
        mock_transcript = Mock()
        mock_transcript.fetch.return_value = mock_transcript_data
        mock_transcript.language_code = 'en'
        
        # Mock transcript list
        mock_transcript_list = Mock()
        mock_transcript_list.find_manually_created_transcript.return_value = mock_transcript
        
        # Mock API
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript_data, video_info = self.fetcher.fetch_transcript(url)
        
        assert transcript_data == mock_transcript_data
        assert isinstance(video_info, dict)
        assert video_info['video_id'] == "dQw4w9WgXcQ"
    
    @patch('talktotube.agents.fetch_transcript.YouTubeTranscriptApi')
    def test_fetch_transcript_no_manual_fallback_to_auto(self, mock_api):
        """Test fallback to auto-generated transcript."""
        # Mock transcript data
        mock_transcript_data = [
            {'text': 'Auto generated', 'start': 0.0, 'duration': 2.0}
        ]
        
        # Mock auto-generated transcript
        mock_auto_transcript = Mock()
        mock_auto_transcript.fetch.return_value = mock_transcript_data
        mock_auto_transcript.language_code = 'en'
        
        # Mock transcript list
        mock_transcript_list = Mock()
        mock_transcript_list.find_manually_created_transcript.side_effect = Exception("No manual transcript")
        mock_transcript_list.find_generated_transcript.return_value = mock_auto_transcript
        
        # Mock API
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript_data, video_info = self.fetcher.fetch_transcript(url)
        
        assert transcript_data == mock_transcript_data
    
    def test_is_transcript_available_invalid_url(self):
        """Test transcript availability check with invalid URL."""
        url = "https://example.com/not-youtube"
        available = self.fetcher.is_transcript_available(url)
        assert available is False
    
    @patch('talktotube.agents.fetch_transcript.YouTubeTranscriptApi')
    def test_is_transcript_available_success(self, mock_api):
        """Test transcript availability check with valid video."""
        # Mock transcript list with available transcripts
        mock_transcript_list = Mock()
        mock_transcript_list.__iter__ = Mock(return_value=iter([Mock(), Mock()]))
        
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        available = self.fetcher.is_transcript_available(url)
        assert available is True
    
    @patch('talktotube.agents.fetch_transcript.YouTubeTranscriptApi')
    def test_is_transcript_available_no_transcripts(self, mock_api):
        """Test transcript availability check with no available transcripts."""
        # Mock transcript list with no transcripts
        mock_transcript_list = Mock()
        mock_transcript_list.__iter__ = Mock(return_value=iter([]))
        
        mock_api.list_transcripts.return_value = mock_transcript_list
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        available = self.fetcher.is_transcript_available(url)
        assert available is False
