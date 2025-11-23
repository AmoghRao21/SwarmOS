from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "SwarmOS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    REDIS_URL: str
    
    OPENAI_API_KEY: str = "not-needed"
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    
    # --- CHANGED TO QWEN ---
    # qwen2.5-coder:7b is the best balance of speed vs smarts for local dev
    OLLAMA_MODEL: str = "qwen2.5-coder:7b" 

    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

@lru_cache
def get_settings() -> Settings:
    return Settings()