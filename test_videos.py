#!/usr/bin/env python3
"""
Test script to find working YouTube videos for TalkToTube.
"""

from talktotube.agents.fetch_transcript import TranscriptFetcher

def test_video_urls():
    """Test various YouTube URLs to find working ones."""
    
    # List of potential test videos
    test_urls = [
        # Educational content
        "https://www.youtube.com/watch?v=ukzFI9rgwfU",  # Khan Academy ML
        "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown Neural Networks
        "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Crash Course Computer Science
        
        # Science content
        "https://www.youtube.com/watch?v=8kK2zwjRV0M",  # Crash Course Biology
        "https://www.youtube.com/watch?v=QOCaacO8wus",  # MinutePhysics
        "https://www.youtube.com/watch?v=YQHsXMglC9A",  # Veritasium
        
        # Tech tutorials
        "https://www.youtube.com/watch?v=Z1Yd7upQsXY",  # Python tutorial
        "https://www.youtube.com/watch?v=rfscVS0vtbw",  # Programming tutorial
        "https://www.youtube.com/watch?v=kqtD5dpn9C8",  # Web development
        
        # Short educational videos
        "https://www.youtube.com/watch?v=Hzg-0GzOsqI",  # Short science
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - Gangnam Style (has captions)
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (classic test)
    ]
    
    fetcher = TranscriptFetcher()
    working_urls = []
    
    print("🧪 Testing YouTube URLs for TalkToTube compatibility...")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Testing: {url}")
        
        # Extract video ID for display
        video_id = fetcher.extract_video_id(url)
        print(f"   Video ID: {video_id}")
        
        # Quick check
        is_accessible, error_msg = fetcher.quick_video_check(url)
        
        if is_accessible:
            print(f"   ✅ ACCESSIBLE: {error_msg}")
            working_urls.append(url)
            
            # Try to get transcript info
            try:
                transcript_data, video_info = fetcher.fetch_transcript(url)
                print(f"   📝 Transcript: {len(transcript_data)} segments")
                print(f"   🎥 Title: {video_info.get('title', 'Unknown')}")
            except Exception as e:
                print(f"   ⚠️  Transcript fetch failed: {str(e)[:100]}...")
        else:
            print(f"   ❌ NOT ACCESSIBLE: {error_msg}")
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {len(working_urls)}/{len(test_urls)} videos are accessible")
    
    if working_urls:
        print("\n✅ Working URLs for testing:")
        for i, url in enumerate(working_urls, 1):
            print(f"   {i}. {url}")
    else:
        print("\n❌ No working URLs found. This might indicate:")
        print("   - Network connectivity issues")
        print("   - YouTube API restrictions")
        print("   - Regional blocking")
        print("   - Temporary YouTube issues")
    
    return working_urls

if __name__ == "__main__":
    working_urls = test_video_urls()
    
    if working_urls:
        print(f"\n🎯 Recommended test URL: {working_urls[0]}")
        print("\n💡 Copy this URL and paste it into TalkToTube!")
    else:
        print("\n🔧 Try these alternative approaches:")
        print("   1. Check your internet connection")
        print("   2. Try again in a few minutes")
        print("   3. Use a VPN if in a restricted region")
        print("   4. Look for educational YouTube channels with captions")
