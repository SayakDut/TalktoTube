# 🎥 TalkToTube - Setup Guide

## ✅ Project Status: READY TO USE!

Your TalkToTube project has been successfully built and tested. All 63 tests are passing, and the Streamlit app is running without errors.

## 🚀 Quick Start

### 1. Virtual Environment (Already Created)
The virtual environment `.venv` has been created and dependencies are installed.

**To activate:**
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

### 2. Environment Configuration
Your HuggingFace API token is already configured in the `.env` file.

### 3. Run the Application
```bash
# Option 1: Direct command
streamlit run app.py

# Option 2: Using batch script (Windows)
run.bat run

# Option 3: Using Makefile (macOS/Linux)
make run
```

The app will be available at: **http://localhost:8501**

## 🧪 Testing

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Basic Functionality Test
```bash
python test_app.py
```

### Current Test Status
- ✅ **63/63 tests passing**
- ✅ All core modules importing correctly
- ✅ Configuration validated
- ✅ Streamlit app starting successfully

## 📋 Features Verified

### ✅ Core Pipeline
- [x] YouTube URL parsing and video ID extraction
- [x] Transcript fetching via youtube-transcript-api
- [x] Audio transcription fallback with yt-dlp + Whisper
- [x] Text normalization and chunking with timestamps
- [x] AI summarization with BART
- [x] Q&A with retrieval-augmented generation
- [x] Embedding-based similarity search

### ✅ UI Components
- [x] Streamlit interface with sidebar controls
- [x] Progress indicators and error handling
- [x] Interactive Q&A chat
- [x] Markdown export functionality
- [x] Configuration sliders and toggles

### ✅ Quality Assurance
- [x] Comprehensive test suite (63 tests)
- [x] Type hints and docstrings
- [x] Error handling and retry logic
- [x] Logging and debugging support

## 🎯 How to Use

1. **Start the app**: `streamlit run app.py`
2. **Open browser**: Go to http://localhost:8501
3. **Paste YouTube URL**: Any public YouTube video
4. **Wait for processing**: The app will:
   - Fetch or transcribe the video
   - Generate AI summary with bullet points
   - Index content for Q&A
5. **Ask questions**: Use the chat interface
6. **Export results**: Copy as Markdown

## 🔧 Configuration Options

The sidebar allows you to adjust:
- **Similarity Threshold**: Minimum confidence for Q&A (0.1-0.8)
- **Top K Chunks**: Number of text segments to retrieve (1-10)
- **Max Duration**: Video length limit for transcription (5-120 min)
- **Translation**: Auto-translate non-English content

## 🛠️ Development Commands

### Windows (Batch Script)
```bash
run.bat setup    # Initial setup
run.bat run      # Start app
run.bat test     # Run tests
run.bat clean    # Clean up
```

### macOS/Linux (Makefile)
```bash
make dev         # Setup development environment
make run         # Start app
make test        # Run tests
make lint        # Code quality checks
make fmt         # Format code
make docker      # Build Docker image
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Run: `pip install -r requirements.txt`

2. **HuggingFace API Errors**
   - Check your API token in `.env`
   - Verify token has access to required models
   - Check rate limits

3. **YouTube Access Issues**
   - Some videos may be private/restricted
   - Try different public videos
   - Check internet connection

### Debug Mode
Enable debug logging by setting in `.env`:
```
TALKTOTUBE_DEBUG=true
```

## 📊 Models Used

- **Transcription**: `openai/whisper-small`
- **Summarization**: `facebook/bart-large-cnn`
- **Q&A**: `google/flan-t5-base`
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`

## 🎉 Success Indicators

If everything is working correctly, you should see:
- ✅ Streamlit app loads without errors
- ✅ Configuration validation passes
- ✅ All 63 tests pass
- ✅ Video processing completes successfully
- ✅ Q&A returns relevant answers with citations

## 📞 Support

If you encounter any issues:
1. Check the logs in the terminal
2. Run `python test_app.py` to verify basic functionality
3. Ensure your HuggingFace token is valid and has API access
4. Try with a simple, public YouTube video first

---

**🚀 TalkToTube is ready to transform your YouTube videos into interactive AI conversations!**
