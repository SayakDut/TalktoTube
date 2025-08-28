#!/usr/bin/env python3
"""
Quick test script to verify TalkToTube works without Streamlit.
"""

import os
import sys

# Set offline mode for testing
os.environ['TALKTOTUBE_OFFLINE'] = 'true'

from talktotube.pipeline import TalkToTubePipeline
from talktotube.demo_data import get_demo_data

def test_pipeline():
    """Test the complete pipeline with demo data."""
    print("🧪 Testing TalkToTube Pipeline")
    print("=" * 50)
    
    try:
        # Initialize pipeline
        print("1. Initializing pipeline...")
        pipeline = TalkToTubePipeline()
        print("   ✅ Pipeline initialized")
        
        # Test with demo URL
        print("\n2. Processing demo video...")
        demo_url = "https://www.youtube.com/watch?v=demo_ml_intro"
        result = pipeline.process_video(demo_url)
        print("   ✅ Video processed successfully")
        
        # Check results
        print(f"\n3. Results:")
        print(f"   📹 Title: {result.video_info.get('title', 'Unknown')}")
        print(f"   🔧 Method: {result.processing_method}")
        print(f"   📝 Chunks: {len(result.chunks)}")
        print(f"   🌐 Language: {result.language}")
        
        # Test summary
        print(f"\n4. Summary:")
        if result.bullet_points:
            for bullet in result.bullet_points[:3]:
                print(f"   {bullet}")
            if len(result.bullet_points) > 3:
                print(f"   ... and {len(result.bullet_points) - 3} more points")
        else:
            print(f"   {result.summary[:100]}...")
        
        # Test Q&A
        print(f"\n5. Testing Q&A...")
        test_questions = [
            "What is machine learning?",
            "What are the types of machine learning?",
            "How do neural networks work?"
        ]
        
        for i, question in enumerate(test_questions, 1):
            answer, citations = pipeline.answer_question(question)
            print(f"   Q{i}: {question}")
            print(f"   A{i}: {answer[:80]}...")
            if citations:
                print(f"   📍 Citations: {len(citations)} found")
        
        print(f"\n✅ All tests passed! TalkToTube is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)
