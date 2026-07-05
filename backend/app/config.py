"""Application settings.

All API keys are backend-only environment variables. They are never exposed
through API responses, logs, or the frontend bundle.
"""
import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    """Pick a writable default DB path.

    On read-only/ephemeral serverless filesystems (e.g. Vercel) only `/tmp`
    is writable, so fall back there. For real persistence set DATABASE_URL to
    an external database (e.g. Postgres) via environment variables.
    """
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return "sqlite:////tmp/alphaquantpro.db"
    return "sqlite:///./alphaquantpro.db"


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

    database_url: str = _default_database_url()


@lru_cache
def get_settings() -> Settings:
    return Settings()
