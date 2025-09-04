# PAI - Interview Reference Guide

## 🎯 Project Overview
**FastAPI AI Task Manager** - Production-ready task management system with dual AI processing architecture

## 🔧 Key Technologies Demonstrated

### Backend Framework
- **FastAPI** - Modern async Python API framework
- **Pydantic** - Data validation with type hints
- **Uvicorn** - ASGI server with hot reload

### AI/ML Integration
- **Pydantic AI** - Type-safe AI agent framework
- **Google Gemini** - Cloud LLM integration (`gemini-1.5-flash`)
- **Ollama** - Local LLM deployment (`phi3:mini`, `tinyllama`)
- **Dual Architecture** - Local-first with cloud fallback

### Infrastructure & DevOps
- **Docker Compose** - Multi-service orchestration
- **Nginx** - Load balancing for LLM instances
- **Health Checks** - Service reliability monitoring
- **Round-Robin Failover** - High availability design

### Observability & Monitoring
- **Prometheus** - Metrics collection (`AI_REQUESTS` counter)
- **Structured Logging** - Contextual logging with `structlog`
- **Background Tasks** - Non-blocking AI processing

## 🏗 Architecture Highlights

### 1. Modular Design Pattern
```
├── models/          # Pydantic schemas & validation
├── services/        # Business logic (DB, AI, LLM)
├── routers/         # API endpoints & HTTP handling
└── dependencies.py  # Dependency injection
```

### 2. AI Service Architecture (`services/ai_service.py`)
- **Primary**: Local Ollama with load balancing
- **Fallback**: Google Gemini via Pydantic AI
- **Testing**: Mock responses for demos
- **Model Selection**: Force specific AI models via API

### 3. Advanced API Features
- **Query Parameters**: Filter by status/priority
- **Background Processing**: Async AI analysis
- **Error Handling**: HTTPException with proper status codes
- **Analytics Endpoint**: Task summary statistics

## 🚀 Technical Implementation Details

### Pydantic AI Integration
```python
# System prompt extraction
def _get_system_prompt(self) -> str:
    return """You are a productivity assistant..."""

# Agent initialization
self.agent = Agent(
    GoogleModel('gemini-1.5-flash', api_key=settings.google_api_key),
    system_prompt=self._get_system_prompt()
)
```

### Local LLM Service (`services/llm_service.py`)
- **Load Balancing**: Round-robin across Ollama instances
- **Health Checking**: Endpoint availability monitoring
- **Failover Logic**: Automatic endpoint switching
- **HTTP Client**: Async requests with `httpx`

### Environment Configuration
- **Pydantic Settings** - Type-safe config management
- **Environment Variables** - `.env` file support
- **Feature Flags** - `USE_LOCAL_LLM` toggle

## 📊 Monitoring & Observability

### Metrics Tracking
```python
AI_REQUESTS = Counter('ai_requests_total', 'AI analysis requests', 
                     ['status', 'model_type'])
```

### Structured Logging
```python
logger.info("ai_analysis_start", task_id=task.id, model_type="local")
```

## 🔀 Key Design Decisions

1. **Local-First AI**: Reduces latency and costs while maintaining cloud fallback
2. **Type Safety**: Pydantic models throughout for runtime validation
3. **Async Architecture**: Non-blocking operations for better performance
4. **Service Isolation**: Clear separation between data, business logic, and API layers
5. **Observability**: Comprehensive logging and metrics for production monitoring

## 🧪 Testing Strategy
- **Pytest** with async support
- **Model Forcing** for testing different AI backends
- **Health Check endpoints** for integration testing

## 📈 Scalability Features
- **Container Orchestration** - Docker Compose for multi-service deployment
- **Load Balancing** - Nginx for LLM instance distribution
- **Stateless Design** - Easy horizontal scaling
- **Background Processing** - Prevents API blocking