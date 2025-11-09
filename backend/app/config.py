"""Configuration settings for HealthGuide backend"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    maps_api_key: str = ""
    database_url: str = "sqlite:///./healthguide.db"
    llm_provider: str = "openai"  # openai or gemini
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

