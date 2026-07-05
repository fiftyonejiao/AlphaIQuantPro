"""Application settings.

All API keys are backend-only environment variables. They are never exposed
through API responses, logs, or the frontend bundle.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # QVeris.ai — the only financial/market data gateway.
    qveris_api_key: str = ""
    qveris_base_url: str = "https://qveris.ai/api/v1"
    qveris_session_id: str = "alphaquantpro-local"

    # DeepSeek — the only LLM runtime. No other provider is supported.
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    database_url: str = "sqlite:///./alphaquantpro.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
