from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str = ""
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///./finance.db"
    chroma_persist_dir: str = "./chroma_data"


settings = Settings()
