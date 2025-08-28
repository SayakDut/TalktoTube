@echo off
echo Starting TalkToTube...
set HUGGINGFACEHUB_API_TOKEN=your_token_here
set TALKTOTUBE_OFFLINE=true
set TALKTOTUBE_DEBUG=false
call .venv\Scripts\activate.bat
streamlit run app.py
