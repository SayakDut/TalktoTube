"""Tests for text chunking functionality."""

import pytest
from talktotube.utils.text import (
    normalize_transcript, 
    chunk_transcript, 
    clean_transcript_text,
    merge_short_segments,
    estimate_tokens,
    parse_timestamp,
    format_timestamp
)


class TestTextProcessing:
    """Test cases for text processing utilities."""
    
    def test_clean_transcript_text_basic(self):
        """Test basic text cleaning."""
        text = "Hello world"
        cleaned = clean_transcript_text(text)
        assert cleaned == "Hello world"
    
    def test_clean_transcript_text_with_tags(self):
        """Test cleaning text with various tags."""
        text = "[Music] Hello world [Applause] (inaudible) <tag>"
        cleaned = clean_transcript_text(text)
        assert cleaned == "Hello world"
    
    def test_clean_transcript_text_with_music_notes(self):
        """Test cleaning text with music notes."""
        text = "♪ Hello world ♪ some text"
        cleaned = clean_transcript_text(text)
        assert cleaned == "some text"
    
    def test_clean_transcript_text_whitespace(self):
        """Test cleaning text with excessive whitespace."""
        text = "  Hello    world  \n\n  "
        cleaned = clean_transcript_text(text)
        assert cleaned == "Hello world"
    
    def test_clean_transcript_text_too_short(self):
        """Test cleaning very short text."""
        text = "Hi"
        cleaned = clean_transcript_text(text)
        assert cleaned == ""
    
    def test_merge_short_segments(self):
        """Test merging short segments."""
        segments = [
            {'text': 'Hi', 'start': 0, 'duration': 1},
            {'text': 'there', 'start': 1, 'duration': 1},
            {'text': 'This is a longer segment', 'start': 2, 'duration': 5}
        ]
        
        merged = merge_short_segments(segments, min_duration=2.0)
        
        assert len(merged) == 2
        assert merged[0]['text'] == 'Hi there'
        assert merged[0]['duration'] >= 2.0
        assert merged[1]['text'] == 'This is a longer segment'
    
    def test_estimate_tokens(self):
        """Test token estimation."""
        text = "Hello world this is a test"
        tokens = estimate_tokens(text)
        assert tokens > 0
        assert tokens == len(text) // 4
    
    def test_parse_timestamp_mm_ss(self):
        """Test parsing MM:SS timestamp."""
        timestamp = "12:34"
        seconds = parse_timestamp(timestamp)
        assert seconds == 12 * 60 + 34
    
    def test_parse_timestamp_hh_mm_ss(self):
        """Test parsing HH:MM:SS timestamp."""
        timestamp = "01:12:34"
        seconds = parse_timestamp(timestamp)
        assert seconds == 1 * 3600 + 12 * 60 + 34
    
    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        timestamp = "invalid"
        seconds = parse_timestamp(timestamp)
        assert seconds == 0.0
    
    def test_format_timestamp_minutes(self):
        """Test formatting timestamp in minutes."""
        seconds = 12 * 60 + 34
        formatted = format_timestamp(seconds)
        assert formatted == "12:34"
    
    def test_format_timestamp_hours(self):
        """Test formatting timestamp with hours."""
        seconds = 1 * 3600 + 12 * 60 + 34
        formatted = format_timestamp(seconds)
        assert formatted == "01:12:34"
    
    def test_normalize_transcript_empty(self):
        """Test normalizing empty transcript."""
        transcript_data = []
        normalized = normalize_transcript(transcript_data)
        assert normalized == ""
    
    def test_normalize_transcript_basic(self):
        """Test normalizing basic transcript."""
        transcript_data = [
            {'text': 'Hello world', 'start': 0, 'duration': 2},
            {'text': 'This is a test', 'start': 2, 'duration': 3}
        ]
        
        normalized = normalize_transcript(transcript_data)
        
        assert '[00:00]' in normalized
        assert 'Hello world' in normalized
        assert '[00:02]' in normalized
        assert 'This is a test' in normalized
    
    def test_normalize_transcript_with_cleaning(self):
        """Test normalizing transcript with text that needs cleaning."""
        transcript_data = [
            {'text': '[Music] Hello world', 'start': 0, 'duration': 2},
            {'text': 'This is a test (inaudible)', 'start': 2, 'duration': 3}
        ]
        
        normalized = normalize_transcript(transcript_data)
        
        assert '[Music]' not in normalized
        assert '(inaudible)' not in normalized
        assert 'Hello world' in normalized
        assert 'This is a test' in normalized
    
    def test_chunk_transcript_empty(self):
        """Test chunking empty transcript."""
        transcript_text = ""
        chunks = chunk_transcript(transcript_text)
        assert len(chunks) == 0
    
    def test_chunk_transcript_basic(self):
        """Test basic transcript chunking."""
        transcript_text = """[00:00] Hello world this is a test
[00:05] This is another segment
[00:10] And this is the final segment"""
        
        chunks = chunk_transcript(transcript_text, chunk_size=50)
        
        assert len(chunks) > 0
        assert all(chunk.text for chunk in chunks)
        assert all(chunk.start_time >= 0 for chunk in chunks)
        assert all(chunk.chunk_id >= 0 for chunk in chunks)
    
    def test_chunk_transcript_with_overlap(self):
        """Test transcript chunking with overlap."""
        transcript_text = """[00:00] First segment
[00:05] Second segment  
[00:10] Third segment
[00:15] Fourth segment"""
        
        chunks = chunk_transcript(transcript_text, chunk_size=30, overlap_percent=0.5)
        
        assert len(chunks) >= 2
        # Check that chunks have reasonable overlap
        if len(chunks) > 1:
            assert chunks[0].end_time <= chunks[1].end_time
    
    def test_chunk_transcript_timestamp_continuity(self):
        """Test that chunk timestamps are in order."""
        transcript_text = """[00:00] First segment
[00:05] Second segment  
[00:10] Third segment
[00:15] Fourth segment
[00:20] Fifth segment"""
        
        chunks = chunk_transcript(transcript_text, chunk_size=40)
        
        # Check timestamp continuity
        for i in range(len(chunks) - 1):
            assert chunks[i].start_time <= chunks[i+1].start_time
    
    def test_chunk_transcript_citation_format(self):
        """Test chunk citation formatting."""
        transcript_text = "[01:23] Test segment"
        chunks = chunk_transcript(transcript_text)
        
        if chunks:
            citation = chunks[0].get_citation()
            assert '[' in citation
            assert ']' in citation
            assert '–' in citation or '-' in citation
