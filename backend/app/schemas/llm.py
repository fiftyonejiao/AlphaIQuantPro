"""Schemas for the DeepSeek-only LLM boundary."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class LLMStatus(BaseModel):
    provider: Literal["deepseek"] = "deepseek"
    configured: bool
    model: str
    base_url: str


class LLMResult(BaseModel):
    text: str
    is_mock: bool = False
    model: str = ""
    provider: Literal["deepseek"] = "deepseek"


class StrategyReviewRequest(BaseModel):
    strategy_id: str
    backtest_id: Optional[str] = None
    language: Literal["en", "zh-CN"] = "en"
    question: Optional[str] = None


class AssistantChatRequest(BaseModel):
    strategy_id: Optional[str] = None
    message: str
    language: Literal["en", "zh-CN"] = "en"
    history: list[dict[str, str]] = Field(default_factory=list)
