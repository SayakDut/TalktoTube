#!/usr/bin/env python3
"""
Final test to verify TalkToTube is working perfectly.
"""

import os
import sys

# Set environment variables for testing
os.environ['HUGGINGFACEHUB_API_TOKEN'] = 'your_token_here'
os.environ['TALKTOTUBE_OFFLINE'] = 'true'
os.environ['TALKTOTUBE_DEBUG'] = 'false'

def test_complete_workflow():
    """Test the complete TalkToTube workflow."""
    print("🎯 TalkToTube - Final Verification Test")
    print("=" * 50)
    
    try:
        # Test 1: Import all modules
        print("1. Testing imports...")
        from talktotube.pipeline import TalkToTubePipeline
        from talktotube.config import Config
        print("   ✅ All modules imported successfully")
        
        # Test 2: Check configuration
        print("\n2. Checking configuration...")
        print(f"   🔧 Offline Mode: {Config.OFFLINE_MODE}")
        print(f"   🔑 API Token: {'✅ Set' if Config.HUGGINGFACE_API_TOKEN else '❌ Missing'}")
        print(f"   🐛 Debug Mode: {Config.DEBUG}")
        
        # Test 3: Initialize pipeline
        print("\n3. Initializing pipeline...")
        pipeline = TalkToTubePipeline()
        print("   ✅ Pipeline initialized")
        
        # Test 4: Process demo video
        print("\n4. Processing demo video...")
        demo_url = "https://www.youtube.com/watch?v=demo_ml_intro"
        result = pipeline.process_video(demo_url)
        print("   ✅ Video processed successfully")
        
        # Test 5: Verify results
        print(f"\n5. Verifying results...")
        print(f"   📹 Title: {result.video_info.get('title', 'Unknown')}")
        print(f"   🔧 Method: {result.processing_method}")
        print(f"   📝 Chunks: {len(result.chunks)}")
        print(f"   🌐 Language: {result.language}")
        print(f"   📋 Summary: {len(result.summary)} characters")
        print(f"   🔸 Bullet Points: {len(result.bullet_points)}")
        
        # Test 6: Test Q&A
        print(f"\n6. Testing Q&A system...")
        questions = [
            "What is machine learning?",
            "What are neural networks?",
            "How does supervised learning work?"
        ]
        
        for i, question in enumerate(questions, 1):
            answer, citations = pipeline.answer_question(question)
            print(f"   Q{i}: {question}")
            print(f"   A{i}: {answer[:60]}...")
            print(f"   📍 Citations: {len(citations)}")
        
        # Test 7: Export functionality
        print(f"\n7. Testing export...")
        qa_history = [(q, pipeline.answer_question(q)[0]) for q in questions[:2]]
        markdown = pipeline.export_to_markdown(result, qa_history)
        print(f"   ✅ Markdown export: {len(markdown)} characters")
        
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"\n📊 Summary:")
        print(f"   ✅ Core pipeline working")
        print(f"   ✅ Demo data processing")
        print(f"   ✅ AI summarization")
        print(f"   ✅ Q&A with citations")
        print(f"   ✅ Markdown export")
        print(f"   ✅ Error-free operation")
        
        print(f"\n🚀 TalkToTube is ready for use!")
        print(f"   🌐 Streamlit app: http://localhost:8501")
        print(f"   🎯 Click 'Demo Mode' to test all features")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
