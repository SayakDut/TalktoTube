# 🎥 TalkToTube

[![CI Status](https://github.com/SayakDut/TalktoTube/workflows/CI/badge.svg)](https://github.com/SayakDut/TalktoTube/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**AI-powered YouTube video analysis and Q&A** - Transform any YouTube video into an interactive chat experience with automatic transcription, intelligent summarization, and citation-backed question answering.

## ✨ Features

- 🎯 **Smart Transcript Fetching** - Automatically retrieves YouTube captions or transcribes audio using Whisper
- 📋 **AI Summarization** - Generates concise bullet-point summaries with timestamps
- 💬 **Interactive Q&A** - Ask questions and get answers with precise video citations
- 🌐 **Multi-language Support** - Handles non-English content with optional translation
- 📤 **Markdown Export** - Export your analysis for documentation and sharing
- 🔒 **Privacy-First** - Runs locally with your own HuggingFace API token

## 🖼️ Screenshots

> **Note**: Screenshots will be added soon to showcase the application's features.

### Key Features Demonstrated:
- **Main Interface** - Clean, professional interface with demo mode
- **Video Processing** - Real-time processing with progress indicators
- **AI Summary** - Intelligent bullet-point summaries with timestamps
- **Interactive Q&A** - Context-aware question answering with citations
- **Export Feature** - Professional Markdown export functionality

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- HuggingFace API token ([Get one here](https://huggingface.co/settings/tokens))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SayakDut/TalktoTube.git
   cd TalktoTube
   ```

2. **Set up virtual environment**
   
   **Windows:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   **Edit the `.env` file and add your HuggingFace token:**
   ```bash
   HUGGINGFACEHUB_API_TOKEN=your_actual_token_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Using Make (Recommended)

```bash
# Set up everything
make dev

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS/Linux)  
source .venv/bin/activate

# Run the app
make run
```

## 🎯 Demo Mode

**Perfect for testing and demonstrations!**

Click the **"🎯 Demo Mode"** button to instantly experience all features:
- ✅ **No API tokens required** - Works completely offline
- ✅ **Instant results** - Pre-loaded with sample ML tutorial content
- ✅ **Full feature showcase** - Test summarization, Q&A, and export
- ✅ **Professional presentation** - Perfect for demos and portfolios

## 💡 Usage

### Standard Workflow
1. **Start the app** and open http://localhost:8501
2. **Paste a YouTube URL** in the input field
3. **Click "Process Video"** and wait for analysis
4. **Review the summary** with key bullet points
5. **Ask questions** in the Q&A section
6. **Export results** as Markdown for sharing

### Quick Demo
1. **Click "🎯 Demo Mode"** for instant results
2. **Explore all features** without setup
3. **Perfect for presentations** and testing

### Sample URLs to Try

- Educational: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- Tech Talk: `https://www.youtube.com/watch?v=example`
- Tutorial: `https://www.youtube.com/watch?v=example`

## 🛠️ Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/test_transcript.py -v
```

### Code Quality

```bash
# Format code
make fmt

# Run linting
make lint

# Run all checks
make check
```

### Docker

```bash
# Build image
make docker

# Run container
make docker-run
```

## 📊 How It Works

1. **Video Processing Pipeline**
   - Extracts video ID from YouTube URL
   - Attempts to fetch existing captions via `youtube-transcript-api`
   - Falls back to audio download + Whisper transcription if needed

2. **Text Processing**
   - Normalizes transcript with timestamp preservation
   - Chunks text into ~1000 token segments with overlap
   - Cleans artifacts and merges short segments

3. **AI Analysis**
   - **Summarization**: Uses BART to generate bullet-point summaries
   - **Embeddings**: Creates vector representations with sentence-transformers
   - **Q&A**: Retrieves relevant chunks and generates answers with FLAN-T5

4. **Smart Retrieval**
   - Cosine similarity search with configurable threshold (default: 0.35)
   - Returns "Not found in video" for low-confidence answers
   - Includes timestamp citations for transparency

## ⚙️ Configuration

Customize behavior via the sidebar:

- **Similarity Threshold**: Minimum confidence for Q&A answers (0.1-0.8)
- **Top K Chunks**: Number of text segments to retrieve (1-10)
- **Max Duration**: Video length limit for transcription (5-120 minutes)
- **Translation**: Auto-translate non-English content to English

## 🔧 API Models Used

- **Transcription**: `openai/whisper-small`
- **Summarization**: `facebook/bart-large-cnn`
- **Q&A**: `google/flan-t5-base`
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`

## 📝 Notes

### Rate Limits
- HuggingFace Inference API has rate limits
- Built-in retry logic with exponential backoff
- Consider upgrading to HF Pro for higher limits

### Privacy
- No data stored on external servers
- All processing happens locally or via your HF token
- Audio files are temporarily downloaded and immediately deleted

### Citations
- All answers include timestamp citations like `[12:34–13:12]`
- Citations link back to specific video segments
- Helps verify AI responses against source material

## 🗺️ Roadmap

- [ ] **Video Player Integration** - Clickable timestamps that jump to video positions
- [ ] **Batch Processing** - Analyze multiple videos at once
- [ ] **Advanced Search** - Semantic search across video libraries
- [ ] **Custom Models** - Support for local/custom AI models
- [ ] **API Mode** - REST API for programmatic access
- [ ] **Collaboration** - Share and collaborate on video analyses

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [HuggingFace](https://huggingface.co/) for the AI models and inference API
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for transcript fetching
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for audio extraction

---

**Built with ❤️ using Python, Streamlit, and HuggingFace**
