import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AgenciAI"
    REDIS_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    class Config:
        env_file = ".env"

settings = Settings()
