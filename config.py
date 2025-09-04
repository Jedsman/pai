from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    google_api_key: Optional[str] = None
    app_name: str = "AI Task Manager"
    debug: bool = False
    use_local_llm: bool = True
    ollama_endpoints: str = "http://localhost:8080"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()