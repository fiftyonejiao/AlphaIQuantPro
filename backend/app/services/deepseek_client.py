"""DeepSeek client — the ONLY LLM runtime for AlphaQuantPro.

No other provider (and no multi-provider fallback) exists in this codebase.
If the key is missing, callers receive clearly marked MOCK LLM OUTPUT so
deterministic features keep working.
"""
from typing import Optional

import httpx

from ..config import get_settings
from ..schemas.llm import LLMResult, LLMStatus

MOCK_PREFIX = "[MOCK LLM OUTPUT] "


class DeepSeekClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key if api_key is not None else settings.deepseek_api_key
        self.base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self.model = model or settings.deepseek_model
        self.timeout = timeout
        if not self.model.startswith("deepseek"):
            raise ValueError(
                "DEEPSEEK_MODEL must be an official DeepSeek model (deepseek-*)."
            )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key) and self.api_key != "your_deepseek_api_key_here"

    def status(self) -> LLMStatus:
        return LLMStatus(
            configured=self.is_configured,
            model=self.model,
            base_url=self.base_url,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1500,
        mock_text: str = "LLM features are disabled because DEEPSEEK_API_KEY is not configured.",
    ) -> LLMResult:
        if not self.is_configured:
            return LLMResult(text=MOCK_PREFIX + mock_text, is_mock=True, model=self.model)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                resp.raise_for_status()
                payload = resp.json()
            text = payload["choices"][0]["message"]["content"]
            return LLMResult(text=text, is_mock=False, model=self.model)
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            return LLMResult(
                text=MOCK_PREFIX + f"DeepSeek call failed ({type(exc).__name__}). " + mock_text,
                is_mock=True,
                model=self.model,
            )
