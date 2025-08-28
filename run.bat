@echo off
REM TalkToTube - Windows Batch Script for Easy Management

if "%1"=="help" goto help
if "%1"=="setup" goto setup
if "%1"=="run" goto run
if "%1"=="test" goto test
if "%1"=="clean" goto clean
if "%1"=="" goto help

:help
echo TalkToTube - AI YouTube Video Analysis
echo.
echo Available commands:
echo   setup  - Set up virtual environment and install dependencies
echo   run    - Run the Streamlit app
echo   test   - Run tests
echo   clean  - Clean up temporary files
echo.
echo Usage: run.bat [command]
goto end

:setup
echo Setting up TalkToTube...
python -m venv .venv
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Copy .env.example to .env
echo 2. Add your HuggingFace API token to .env
echo 3. Run: run.bat run
goto end

:run
echo Starting TalkToTube...
call .venv\Scripts\activate.bat
streamlit run app.py
goto end

:test
echo Running tests...
call .venv\Scripts\activate.bat
python -m pytest tests/ -v
goto end

:clean
echo Cleaning up...
rmdir /s /q __pycache__ 2>nul
rmdir /s /q .pytest_cache 2>nul
rmdir /s /q .mypy_cache 2>nul
rmdir /s /q .ruff_cache 2>nul
del /q *.pyc 2>nul
echo Cleanup complete!
goto end

:end
