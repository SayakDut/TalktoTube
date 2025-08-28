"""Text processing utilities for transcript cleaning, chunking, and timestamp handling."""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from ..config import Config

logger = logging.getLogger(__name__)


@dataclass
class TranscriptChunk:
    """A chunk of transcript with metadata."""
    text: str
    start_time: float
    end_time: float
    chunk_id: int
    
    def format_timestamp(self, seconds: float) -> str:
        """Format seconds to MM:SS or HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    def get_citation(self) -> str:
        """Get formatted citation with timestamps."""
        start_str = self.format_timestamp(self.start_time)
        end_str = self.format_timestamp(self.end_time)
        return f"[{start_str}–{end_str}]"


def normalize_transcript(transcript_data: List[Dict[str, Any]]) -> str:
    """
    Normalize transcript data from youtube-transcript-api or Whisper.
    
    Args:
        transcript_data: List of transcript segments with 'text', 'start', 'duration'
        
    Returns:
        Normalized transcript text with timestamps preserved
    """
    if not transcript_data:
        return ""
    
    normalized_segments = []
    
    for segment in transcript_data:
        text = segment.get('text', '').strip()
        if not text:
            continue
            
        # Clean up text
        text = clean_transcript_text(text)
        if not text:
            continue
            
        # Preserve timing information
        start_time = segment.get('start', 0)
        duration = segment.get('duration', 0)
        
        normalized_segments.append({
            'text': text,
            'start': start_time,
            'duration': duration
        })
    
    # Merge short segments
    merged_segments = merge_short_segments(normalized_segments)
    
    # Convert to text with timestamps
    result_parts = []
    for segment in merged_segments:
        start_str = format_timestamp(segment['start'])
        text = segment['text']
        result_parts.append(f"[{start_str}] {text}")
    
    return "\n".join(result_parts)


def clean_transcript_text(text: str) -> str:
    """
    Clean transcript text by removing non-speech elements.
    
    Args:
        text: Raw transcript text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove common non-speech tags and artifacts
    text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
    text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
    text = re.sub(r'<.*?>', '', text)    # Remove HTML-like tags
    text = re.sub(r'♪.*?♪', '', text)    # Remove music notes
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # Remove very short segments (likely artifacts)
    if len(text) < 3:
        return ""
    
    return text


def merge_short_segments(segments: List[Dict[str, Any]], min_duration: float = 2.0) -> List[Dict[str, Any]]:
    """
    Merge short segments to create more coherent chunks.
    
    Args:
        segments: List of transcript segments
        min_duration: Minimum duration for a segment
        
    Returns:
        List of merged segments
    """
    if not segments:
        return []
    
    merged = []
    current_segment = segments[0].copy()
    
    for next_segment in segments[1:]:
        current_duration = current_segment['duration']
        
        # If current segment is too short, merge with next
        if current_duration < min_duration:
            # Merge text
            current_segment['text'] += " " + next_segment['text']
            # Update duration to include next segment
            next_end = next_segment['start'] + next_segment['duration']
            current_end = current_segment['start'] + current_segment['duration']
            current_segment['duration'] = max(next_end, current_end) - current_segment['start']
        else:
            # Current segment is long enough, save it and start new one
            merged.append(current_segment)
            current_segment = next_segment.copy()
    
    # Add the last segment
    merged.append(current_segment)
    
    return merged


def format_timestamp(seconds: float) -> str:
    """Format seconds to MM:SS or HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text (rough approximation).
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    # Rough approximation: 1 token ≈ 4 characters for English
    return len(text) // 4


def chunk_transcript(transcript_text: str, chunk_size: int = None, overlap_percent: float = None) -> List[TranscriptChunk]:
    """
    Chunk transcript into overlapping segments with preserved timestamps.
    
    Args:
        transcript_text: Normalized transcript with timestamps
        chunk_size: Target chunk size in tokens (defaults to config)
        overlap_percent: Overlap percentage (defaults to config)
        
    Returns:
        List of transcript chunks
    """
    chunk_size = chunk_size or Config.CHUNK_SIZE_TOKENS
    overlap_percent = overlap_percent or Config.CHUNK_OVERLAP_PERCENT
    
    # Parse transcript lines with timestamps
    lines = transcript_text.strip().split('\n')
    segments = []
    
    for line in lines:
        if not line.strip():
            continue
            
        # Extract timestamp and text
        match = re.match(r'\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.*)', line)
        if match:
            timestamp_str, text = match.groups()
            start_time = parse_timestamp(timestamp_str)
            segments.append({
                'text': text,
                'start_time': start_time,
                'line': line
            })
    
    if not segments:
        logger.warning("No valid segments found in transcript")
        return []
    
    # Create chunks
    chunks = []
    chunk_id = 0
    i = 0
    
    while i < len(segments):
        chunk_text_parts = []
        chunk_start_time = segments[i]['start_time']
        chunk_end_time = chunk_start_time
        current_tokens = 0
        
        # Add segments to chunk until we reach target size
        j = i
        while j < len(segments) and current_tokens < chunk_size:
            segment = segments[j]
            segment_text = segment['text']
            segment_tokens = estimate_tokens(segment_text)
            
            if current_tokens + segment_tokens <= chunk_size or len(chunk_text_parts) == 0:
                chunk_text_parts.append(segment_text)
                chunk_end_time = segment['start_time']
                current_tokens += segment_tokens
                j += 1
            else:
                break
        
        # Create chunk
        chunk_text = " ".join(chunk_text_parts)
        if chunk_text.strip():
            chunks.append(TranscriptChunk(
                text=chunk_text,
                start_time=chunk_start_time,
                end_time=chunk_end_time,
                chunk_id=chunk_id
            ))
            chunk_id += 1
        
        # Calculate overlap for next chunk
        overlap_segments = max(1, int(len(chunk_text_parts) * overlap_percent))
        i = max(i + 1, j - overlap_segments)
    
    logger.info(f"Created {len(chunks)} chunks from transcript")
    return chunks


def parse_timestamp(timestamp_str: str) -> float:
    """
    Parse timestamp string to seconds.
    
    Args:
        timestamp_str: Timestamp in MM:SS or HH:MM:SS format
        
    Returns:
        Time in seconds
    """
    parts = timestamp_str.split(':')
    
    if len(parts) == 2:  # MM:SS
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:  # HH:MM:SS
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        logger.warning(f"Invalid timestamp format: {timestamp_str}")
        return 0.0
