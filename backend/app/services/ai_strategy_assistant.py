"""AI strategy assistant — DeepSeek-backed chat helper for strategy work.

Assistant output is advisory text only; it can never place orders or alter
deterministic engine behavior.
"""
from typing import Any, Optional

from ..schemas.llm import LLMResult
from .llm_service import LLMService


class AIStrategyAssistant:
    def __init__(self, llm: Optional[LLMService] = None) -> None:
        self.llm = llm or LLMService()

    def chat(
        self,
        message: str,
        strategy: Optional[dict[str, Any]] = None,
        history: Optional[list[dict[str, str]]] = None,
        language: str = "en",
    ) -> LLMResult:
        return self.llm.assistant_chat(
            message=message, strategy=strategy, history=history, language=language
        )

    def review_strategy(
        self,
        strategy: dict[str, Any],
        backtest_result: Optional[dict[str, Any]] = None,
        language: str = "en",
        question: Optional[str] = None,
    ) -> LLMResult:
        return self.llm.generate_strategy_review(
            strategy=strategy,
            backtest_result=backtest_result,
            language=language,
            question=question,
        )
