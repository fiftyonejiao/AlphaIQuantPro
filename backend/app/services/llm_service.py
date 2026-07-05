"""All LLM prompts and orchestration live behind this DeepSeek boundary.

DeepSeek reasons over deterministic engine outputs (metrics, trades, logs);
it never produces prices, fills, indicators, or metrics itself.
"""
import json
from typing import Any, Optional

from ..schemas.llm import LLMResult
from .deepseek_client import DeepSeekClient

_LANG_INSTRUCTIONS = {
    "en": "Respond in English.",
    "zh-CN": "请使用简体中文回答。",
}

_SYSTEM = (
    "You are the AI strategy analyst inside AlphaQuantPro, a quant strategy workbench. "
    "You are given deterministic backtest/paper-run outputs (metrics, trades, logs) computed "
    "by the engine. NEVER invent market data, prices, fills, or metrics; only reason over the "
    "provided numbers. Be concrete, structured, and honest about uncertainty. "
    "Always remind the user this is not financial advice."
)


class LLMService:
    def __init__(self, client: Optional[DeepSeekClient] = None) -> None:
        self.client = client or DeepSeekClient()

    def status(self):
        return self.client.status()

    def _lang(self, language: str) -> str:
        return _LANG_INSTRUCTIONS.get(language, _LANG_INSTRUCTIONS["en"])

    def generate_run_analysis(
        self,
        run_summary: dict[str, Any],
        language: str = "en",
    ) -> LLMResult:
        prompt = (
            "Analyze this paper/simulation run and produce a post-run analysis with: "
            "1) performance summary, 2) risk observations (drawdown, exposure), "
            "3) trade-behavior observations, 4) concrete improvement suggestions. "
            f"{self._lang(language)}\n\nRun data (deterministic engine output):\n"
            + json.dumps(run_summary, default=str)[:8000]
        )
        return self.client.chat(
            [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": prompt}],
            mock_text=(
                "Deterministic run summary: "
                f"final equity {run_summary.get('current_equity')}, "
                f"trades {len(run_summary.get('trades', []))}. "
                "Configure DEEPSEEK_API_KEY for AI-generated analysis."
            ),
        )

    def generate_strategy_review(
        self,
        strategy: dict[str, Any],
        backtest_result: Optional[dict[str, Any]] = None,
        language: str = "en",
        question: Optional[str] = None,
    ) -> LLMResult:
        parts = [
            "Review this trading strategy. Cover: logic soundness, overfitting risk, "
            "risk management gaps, and 3 specific improvement ideas. "
            f"{self._lang(language)}",
            "Strategy:\n" + json.dumps(
                {
                    "name": strategy.get("name"),
                    "type": strategy.get("strategy_type"),
                    "parameters": strategy.get("parameters"),
                    "code": (strategy.get("code") or "")[:4000],
                },
                default=str,
            ),
        ]
        if backtest_result:
            parts.append(
                "Deterministic backtest metrics (engine-computed):\n"
                + json.dumps(backtest_result.get("metrics", {}), default=str)
            )
        if question:
            parts.append("User question: " + question)
        return self.client.chat(
            [{"role": "system", "content": _SYSTEM}, {"role": "user", "content": "\n\n".join(parts)}],
            mock_text=(
                f"Strategy '{strategy.get('name')}' review is unavailable without a DeepSeek key. "
                "The deterministic backtest metrics above remain fully valid."
            ),
        )

    def assistant_chat(
        self,
        message: str,
        strategy: Optional[dict[str, Any]] = None,
        history: Optional[list[dict[str, str]]] = None,
        language: str = "en",
    ) -> LLMResult:
        messages: list[dict[str, str]] = [{"role": "system", "content": _SYSTEM + " " + self._lang(language)}]
        if strategy:
            messages.append(
                {
                    "role": "system",
                    "content": "Current strategy context:\n"
                    + json.dumps(
                        {
                            "name": strategy.get("name"),
                            "type": strategy.get("strategy_type"),
                            "parameters": strategy.get("parameters"),
                            "code": (strategy.get("code") or "")[:3000],
                        },
                        default=str,
                    ),
                }
            )
        for turn in (history or [])[-8:]:
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": message})
        return self.client.chat(
            messages,
            mock_text="The AI strategy assistant needs DEEPSEEK_API_KEY to respond.",
        )
