# Project Structure:
# ├── main.py
# ├── models/
# │   ├── __init__.py
# │   └── task_models.py
# ├── services/
# │   ├── __init__.py
# │   ├── ai_service.py
# │   └── database.py
# ├── routers/
# │   ├── __init__.py
# │   ├── tasks.py
# │   └── health.py
# └── dependencies.py

# Initialize project
uv init ai-task-manager
cd ai-task-manager

# Add dependencies
uv add fastapi uvicorn[standard] pydantic pydantic-settings pydantic-ai google-generativeai

# Add dev dependencies
uv add --dev pytest pytest-asyncio httpx ruff mypy

# Run the app
uv run uvicorn main:app --reload

# Install from pyproject.toml
uv sync

# Run all tests
uv run pytest

# Run with coverage and verbose output
uv run pytest -v --tb=short

# Run specific test file
uv run pytest tests/test_tasks.py

# Format/lint
uv run ruff check
uv run mypy .

# Local
docker build -t task-manager .

# GPU version for GKE  
docker build -f Dockerfile.gpu -t task-manager:gpu .


# Install
helm install ai-task-manager ./helm

# Upgrade
helm upgrade ai-task-manager ./helm --set image.tag=v2.0.0

# Different environments  
helm install ai-task-manager ./helm -f values-production.yaml

# Start local LLM infrastructure
docker-compose -f docker-compose.local-llm.yml up -d

# Check health
curl http://localhost:8080/health
curl http://localhost:8000/health