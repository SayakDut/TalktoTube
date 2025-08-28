#!/usr/bin/env python3
"""
Simple test script to verify TalkToTube functionality without UI.
This script tests the core pipeline components.
"""

import os
import sys
from talktotube.config import Config, validate_config
from talktotube.agents.fetch_transcript import TranscriptFetcher
from talktotube.utils.text import normalize_transcript, chunk_transcript


def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("🧪 Testing TalkToTube Core Functionality")
    print("=" * 50)
    
    # Test 1: Configuration
    print("1. Testing configuration...")
    try:
        validate_config()
        print("   ✅ Configuration is valid")
        print(f"   📝 HuggingFace token: {'✅ Set' if Config.HUGGINGFACE_API_TOKEN else '❌ Missing'}")
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")
        return False
    
    # Test 2: Video ID extraction
    print("\n2. Testing video ID extraction...")
    fetcher = TranscriptFetcher()
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ"
    ]
    
    for url in test_urls:
        video_id = fetcher.extract_video_id(url)
        if video_id == "dQw4w9WgXcQ":
            print(f"   ✅ {url} → {video_id}")
        else:
            print(f"   ❌ {url} → {video_id}")
            return False
    
    # Test 3: Text processing
    print("\n3. Testing text processing...")
    sample_transcript = [
        {'text': 'Hello world', 'start': 0, 'duration': 2},
        {'text': 'This is a test', 'start': 2, 'duration': 3},
        {'text': 'Testing transcript processing', 'start': 5, 'duration': 4}
    ]
    
    normalized = normalize_transcript(sample_transcript)
    if normalized and '[00:00]' in normalized and 'Hello world' in normalized:
        print("   ✅ Transcript normalization works")
    else:
        print("   ❌ Transcript normalization failed")
        return False
    
    # Test 4: Text chunking
    chunks = chunk_transcript(normalized)
    if chunks and len(chunks) > 0:
        print(f"   ✅ Text chunking works ({len(chunks)} chunks created)")
        print(f"   📝 First chunk: {chunks[0].text[:50]}...")
    else:
        print("   ❌ Text chunking failed")
        return False
    
    print("\n🎉 All basic tests passed!")
    print("\n📋 Next Steps:")
    print("   1. The Streamlit app is running at http://localhost:8501")
    print("   2. Paste a YouTube URL to test the full pipeline")
    print("   3. Make sure your HuggingFace token has access to the required models")
    
    return True


def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        'talktotube.config',
        'talktotube.pipeline',
        'talktotube.ui',
        'talktotube.agents.fetch_transcript',
        'talktotube.agents.transcribe_fallback',
        'talktotube.agents.summarize',
        'talktotube.agents.qa',
        'talktotube.utils.text',
        'talktotube.utils.retrieval'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module}: {e}")
            return False
    
    return True


if __name__ == "__main__":
    print("🎥 TalkToTube - Test Script")
    print("=" * 50)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed!")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality tests failed!")
        sys.exit(1)
    
    print("\n✅ All tests completed successfully!")
    print("\n🚀 TalkToTube is ready to use!")
