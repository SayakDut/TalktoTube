# TalkToTube Makefile

.PHONY: help dev install run test lint fmt clean docker docker-run

# Default target
help:
	@echo "TalkToTube - AI YouTube Video Analysis"
	@echo ""
	@echo "Available targets:"
	@echo "  dev        - Set up development environment"
	@echo "  install    - Install dependencies"
	@echo "  run        - Run the Streamlit app"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting (ruff + mypy)"
	@echo "  fmt        - Format code (black + ruff)"
	@echo "  clean      - Clean up temporary files"
	@echo "  docker     - Build Docker image"
	@echo "  docker-run - Run Docker container"

# Development environment setup
dev: .venv
	@echo "Development environment ready!"
	@echo ""
	@echo "Activation commands:"
	@echo "  Windows: .venv\\Scripts\\activate"
	@echo "  macOS/Linux: source .venv/bin/activate"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Activate the virtual environment"
	@echo "  2. Copy .env.example to .env and add your HuggingFace token"
	@echo "  3. Run 'make run' to start the app"

# Create virtual environment and install dependencies
.venv:
	python -m venv .venv
	@echo "Virtual environment created. Installing dependencies..."
	.venv/Scripts/pip install --upgrade pip
	.venv/Scripts/pip install -r requirements.txt
	@echo "Dependencies installed!"

# Install dependencies (assumes venv is activated)
install:
	pip install --upgrade pip
	pip install -r requirements.txt

# Run the Streamlit app
run:
	streamlit run app.py

# Run tests
test:
	pytest -v --tb=short

# Run tests with coverage
test-cov:
	pytest --cov=talktotube --cov-report=html --cov-report=term

# Linting
lint:
	ruff check .
	mypy .

# Format code
fmt:
	black .
	ruff check --fix .

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete

# Docker targets
docker:
	docker build -t talktotube .

docker-run:
	docker run -p 8501:8501 --env-file .env talktotube

# Development workflow
check: fmt lint test
	@echo "All checks passed!"

# Install pre-commit hooks
pre-commit:
	pre-commit install

# Update dependencies
update-deps:
	pip list --outdated
	@echo "Review outdated packages above and update requirements.txt manually"
