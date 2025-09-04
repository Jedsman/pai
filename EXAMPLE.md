# Local LLM Complete Example

## Setup

```bash
# 1. Start the infrastructure
docker-compose -f docker-compose.local-llm.yml up -d

# 2. Wait for models to download (2-3 minutes)
docker logs ollama-1 -f  # Watch download progress

# Pull models to both containers
docker exec ollama-1 ollama pull phi3:mini
docker exec ollama-2 ollama pull tinyllama

# Test they're available
curl http://localhost:11434/api/tags
curl http://localhost:11435/api/tags

# 3. Check health
curl http://localhost:8080/health    # Load balancer
curl http://localhost:11434/api/tags  # Ollama-1
curl http://localhost:11435/api/tags  # Ollama-2
curl http://localhost:8000/health       # FastAPI app
```

## Test Local LLM

```bash
# Test direct Ollama
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:mini",
    "prompt": "Write a brief task suggestion:",
    "stream": false
  }'

# Test load balancer
curl -X POST http://localhost:8080/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:mini", 
    "prompt": "How to organize daily tasks?",
    "stream": false
  }'
```

## Use with Task Manager

```bash
# 1. Create a task
curl -X POST "http://localhost:8000/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add JWT-based auth to the API",
    "priority": "high"
  }'

# Response includes task ID
# {
#   "id": 1,
#   "title": "Implement user authentication",
#   "status": "todo",
#   ...
# }

# 2. Get AI suggestion (uses local LLM)
curl "http://localhost:8000/tasks/1/ai-suggestion"

# Response from local LLM:
# {
#   "suggestion": "Start by researching JWT libraries for your framework. Break into steps: 1) Set up JWT token generation, 2) Create login endpoint, 3) Add middleware for protected routes, 4) Test with Postman. Focus on security best practices from the start."
# }
```

# Force local LLM
curl "http://localhost:8000/tasks/1/ai-suggestion?model=local"

# Force cloud LLM  
curl "http://localhost:8000/tasks/1/ai-suggestion?model=cloud"

# Force mock
curl "http://localhost:8000/tasks/1/ai-suggestion?model=mock"

## Verify Local Processing

```bash
# Check logs to see which model was used
docker logs ai-task-manager | grep "ai_analysis"

# Example log output:
# {"event": "ai_analysis_start", "task_id": 1, "model_type": "local"}
# {"event": "ai_analysis_complete", "task_id": 1, "model_type": "local"}
```

## Test Failover

```bash
# Stop one Ollama instance
docker stop ollama-1

# Request still works (routes to ollama-2)
curl "http://localhost:8000/tasks/1/ai-suggestion"

# Stop all local LLMs
docker stop ollama-2

# Falls back to cloud LLM (if GOOGLE_API_KEY set) or mock
curl "http://localhost:8000/tasks/1/ai-suggestion"
```

## Monitor Performance

```bash
# Check metrics
curl "http://localhost:8000/metrics" | grep ai_requests

# Example output:
# ai_requests_total{model_type="local",status="success"} 5.0
# ai_requests_total{model_type="cloud",status="success"} 1.0
# ai_requests_total{model_type="fallback",status="mock"} 0.0
```

## Environment Variables

```bash
# Use only local LLMs
export USE_LOCAL_LLM=true

# Disable local, use cloud only  
export USE_LOCAL_LLM=false
export GOOGLE_API_KEY=your-key

# Custom Ollama endpoint
export OLLAMA_ENDPOINTS=http://localhost:8080
```

## Cleanup

```bash
# Stop all containers
docker-compose -f docker-compose.local-llm.yml down

# Remove volumes (deletes downloaded models)
docker-compose -f docker-compose.local-llm.yml down -v
```