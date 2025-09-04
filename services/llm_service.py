import httpx
import asyncio
from typing import List, Optional
import structlog
from config import settings

logger = structlog.get_logger()

class LocalLLMService:
    def __init__(self):
        self.endpoints = [
            "http://localhost:11434",  # ollama-1
            "http://localhost:11435",  # ollama-2
        ]
        self.load_balancer_url = "http://localhost:8080"
        self.current_endpoint = 0
        
    async def health_check(self, endpoint: str) -> bool:
        """Check if LLM endpoint is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{endpoint}/api/health")
                return response.status_code == 200
        except:
            return False
    
    async def get_healthy_endpoint(self) -> Optional[str]:
        """Get next healthy endpoint using round-robin"""
        for _ in range(len(self.endpoints)):
            endpoint = self.endpoints[self.current_endpoint]
            self.current_endpoint = (self.current_endpoint + 1) % len(self.endpoints)
            
            if await self.health_check(endpoint):
                return endpoint
        return None
    
    async def generate_completion(self, prompt: str, model: str = "phi3:mini") -> str:
        """Generate completion with failover"""
        # Try load balancer first
        try:
            return await self._call_ollama(self.load_balancer_url, prompt, model)
        except Exception as e:
            logger.warning("load_balancer_failed", error=str(e))
        
        # Fallback to direct endpoints
        endpoint = await self.get_healthy_endpoint()
        if not endpoint:
            raise Exception("No healthy LLM endpoints available")
        
        return await self._call_ollama(endpoint, prompt, model)
    
    async def _call_ollama(self, endpoint: str, prompt: str, model: str) -> str:
        """Call Ollama API"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 100
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]