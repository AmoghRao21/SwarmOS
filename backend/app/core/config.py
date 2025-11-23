from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "SwarmOS"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    POSTGRES_USER: str = "swarm_admin"
    POSTGRES_PASSWORD: str = "swarm_secure_password"
    POSTGRES_DB: str = "swarm_core"
    DATABASE_URL: str = "" # Will be populated by environment variables

    REDIS_URL: str = "redis://redis:6379/0"
    
    # --- BRAIN CONFIGURATION ---
    GROQ_API_KEY: str = "" # Must be set in .env
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    CORS_ORIGINS: list[str] = ["*"]

@lru_cache
def get_settings() -> Settings:
    return Settings()