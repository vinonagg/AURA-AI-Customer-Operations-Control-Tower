from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    log_level: str = "INFO"
    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-luna"
    embedding_model: str = "text-embedding-3-small"
    database_url: str = "sqlite:///./aura.db"
    autonomous_compensation_limit_inr: float = 1000.0
    confidence_auto_execute: float = 0.85
    aura_api_url: str = "http://127.0.0.1:8010"
    enable_llm_enrichment: bool = True
    enable_semantic_rag: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
