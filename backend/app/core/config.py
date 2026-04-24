from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM Configuration
    llm_provider: str = "ollama"
    ollama_model: str = "mistral"
    ollama_base_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""
    claude_model: str = "claude-haiku-4-5"

    # External APIs
    newsapi_key: str = ""
    alpha_vantage_key: str = ""

    # Data Storage
    chroma_persist_dir: str = "./chroma_db"
    database_url: str = "sqlite:///./finance.db"

    # App
    app_env: str = "development"
    log_level: str = "INFO"


settings = Settings()

# Ensure chroma directory exists
Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
