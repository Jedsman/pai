from typing import Optional
from fastapi import HTTPException
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from models.task_models import Task
from config import settings
from .llm_service import LocalLLMService
import structlog
from prometheus_client import Counter

logger = structlog.get_logger()
AI_REQUESTS = Counter('ai_requests_total', 'AI analysis requests', ['status', 'model_type'])

class AITaskAnalyzer:
    def __init__(self):
        self.local_llm = LocalLLMService()
        
        # Google Gemini fallback
        if settings.google_api_key:
            try:
                self.agent = Agent(
                    GoogleModel('gemini-1.5-flash', api_key=settings.google_api_key),
                    system_prompt=self._get_system_prompt()
                )
            except Exception:
                self.agent = None
        else:
            self.agent = None
    
    def _get_system_prompt(self) -> str:
        return """You are a productivity assistant. Given a task description, 
        provide a brief, actionable suggestion to help complete it efficiently. 
        Keep responses under 100 words."""
    
    async def analyze_task(self, task: Task, force_model: Optional[str] = None) -> str:
        """Generate AI suggestion with model selection"""
        if force_model == "mock":
            AI_REQUESTS.labels(status="mock", model_type="fallback").inc()
            return self._mock_suggestion(task)
        
        if force_model == "cloud":
            if self.agent:
                try:
                    return await self._analyze_with_cloud_llm(task)
                except Exception as e:
                    logger.error("forced_cloud_llm_failed", task_id=task.id, error=str(e))
            return self._mock_suggestion(task)
        
        if force_model == "local" or (settings.use_local_llm and not force_model):
            try:
                return await self._analyze_with_local_llm(task)
            except Exception as e:
                logger.warning("local_llm_failed", task_id=task.id, error=str(e))
                if force_model == "local":
                    raise HTTPException(status_code=503, detail="Local LLM unavailable")
        
        # Auto fallback logic (unchanged)
        if self.agent and not force_model:
            try:
                return await self._analyze_with_cloud_llm(task)
            except Exception as e:
                logger.error("cloud_llm_failed", task_id=task.id, error=str(e))
        
        AI_REQUESTS.labels(status="mock", model_type="fallback").inc()
        return self._mock_suggestion(task)
    
    async def _analyze_with_local_llm(self, task: Task) -> str:
        """Use local Ollama for analysis"""
        logger.info("ai_analysis_start", task_id=task.id, model_type="local")
        
        prompt = f"""{self._get_system_prompt()}

Task: {task.title}
Description: {task.description or 'No description'}
Priority: {task.priority.value}
Due: {task.due_date or 'No deadline'}

Suggest how to approach this task effectively:"""
        
        result = await self.local_llm.generate_completion(prompt)
        AI_REQUESTS.labels(status="success", model_type="local").inc()
        
        logger.info("ai_analysis_complete", task_id=task.id, model_type="local")
        return result.strip()
    
    async def _analyze_with_cloud_llm(self, task: Task) -> str:
        """Use Google Gemini for analysis"""
        logger.info("ai_analysis_start", task_id=task.id, model_type="cloud")
        
        prompt = f"""Task: {task.title}
        Description: {task.description or 'No description'}
        Priority: {task.priority.value}
        Due: {task.due_date or 'No deadline'}
        
        Suggest how to approach this task effectively."""
        
        result = await self.agent.run(prompt)
        AI_REQUESTS.labels(status="success", model_type="cloud").inc()
        
        logger.info("ai_analysis_complete", task_id=task.id, model_type="cloud")
        return result.data
    
    def _mock_suggestion(self, task: Task) -> str:
        """Mock suggestions for demo"""
        suggestions = {
            "high": "🔥 High priority! Break this into smaller chunks and tackle immediately.",
            "medium": "📋 Consider time-blocking 30-45 minutes to focus on this task.",
            "low": "⏰ Schedule this for a quiet time when you have mental bandwidth."
        }
        return suggestions.get(task.priority.value, "Focus on one step at a time.")