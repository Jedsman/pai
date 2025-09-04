
## Development Commands

### Package Management & Dependencies
- `uv sync` - Install dependencies from pyproject.toml
- `uv add <package>` - Add runtime dependency
- `uv add --dev <package>` - Add development dependency

### Running the Application
- `uv run uvicorn main:app --reload` - Start development server with auto-reload
- `uv run python main.py` - Alternative way to start the server
- Default server runs on http://localhost:8000

### Local LLM Infrastructure
- `docker-compose -f docker-compose.local-llm.yml up -d` - Start local Ollama LLM infrastructure
- `curl http://localhost:8080/health` - Check load balancer health
- `curl http://localhost:8000/health` - Check API health
- Uses Ollama with phi3:mini and tinyllama models for local AI processing
- Health checks now use `/api/tags` endpoint for better reliability

### Testing
- `uv run pytest` - Run all tests
- `uv run pytest -v --tb=short` - Run tests with verbose output and short traceback
- `uv run pytest tests/test_tasks.py` - Run specific test file
- `uv run pytest tests/test_models.py -v` - Run specific test with verbose output

### Code Quality & Linting
- `uv run ruff check` - Run linting checks
- `uv run mypy .` - Run type checking

### Docker
- `docker build -t task-manager .` - Build standard Docker image
- `docker build -f Dockerfile.gpu -t task-manager:gpu .` - Build GPU-enabled image

### Kubernetes/Helm
- `helm install ai-task-manager ./helm` - Install application
- `helm upgrade ai-task-manager ./helm --set image.tag=v2.0.0` - Upgrade deployment

## Architecture Overview

This is a FastAPI-based AI Task Manager with a modular architecture:

### Core Structure
- **main.py**: FastAPI application entry point with CORS middleware and router registration
- **config.py**: Pydantic Settings for environment configuration (Google API key, debug mode)
- **dependencies.py**: Global dependency injection for database and AI services

### Modular Components
- **models/**: Pydantic models defining task schemas, enums (Priority, TaskStatus), and validation
- **services/**: Business logic layer containing TaskDatabase and AITaskAnalyzer services  
- **routers/**: FastAPI route handlers for tasks and health endpoints

### Key Features
- Task CRUD operations with optional filtering by status/priority
- **Dual AI Architecture**: Local LLM (Ollama) with cloud fallback (Google Gemini)
- Load-balanced local AI processing with automatic failover
- Task analytics and summary statistics with Prometheus metrics
- In-memory database implementation (TaskDatabase service)
- Comprehensive validation with due date constraints
- Structured logging with contextual information

### API Endpoints
- `/tasks` - Full CRUD for task management
- `/tasks/{id}/ai-suggestion?model={local|cloud|mock}` - AI analysis with model selection
- `/tasks/analytics/summary` - Task statistics and summaries
- `/health` - Health check endpoint

### AI Processing Architecture
The system now supports dual AI processing modes:

1. **Local LLM (Primary)**: Uses Ollama with load balancing across multiple instances
   - Models: phi3:mini, tinyllama for fast local processing
   - Round-robin failover between endpoints (localhost:11434, localhost:11435)
   - Load balancer on localhost:8080 with health checking

2. **Cloud LLM (Fallback)**: Google Gemini via Pydantic AI
   - Automatic fallback when local LLM is unavailable
   - Uses `gemini-1.5-flash` model with structured prompting

3. **Model Selection**: API supports forcing specific AI models via `force_model` parameter
   - `model=local` - Forces local Ollama processing (returns 503 if unavailable)
   - `model=cloud` - Forces Google Gemini processing
   - `model=mock` - Returns predefined suggestions for testing
   - Default: Auto-fallback from local → cloud → mock

4. **System Prompt**: Extracted to `_get_system_prompt()` method in `services/ai_service.py:28-31`

### Dependencies
- Uses `uv` for package management
- FastAPI with Pydantic for API and data validation
- **New**: Ollama for local LLM processing with httpx client
- **New**: Prometheus metrics for monitoring AI requests
- **New**: Structlog for structured logging
- Google Generative AI for cloud fallback
- Pytest for testing with async support
- Ruff for linting, MyPy for type checking

### Environment Setup
- `.env` file with `GOOGLE_API_KEY` for cloud AI fallback
- `USE_LOCAL_LLM=true` to enable local processing (default)
- `OLLAMA_ENDPOINTS=http://localhost:8080` for load balancer URL