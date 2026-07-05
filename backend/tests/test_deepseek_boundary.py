import pathlib

import pytest

from app.config import Settings
from app.services.ai_strategy_assistant import AIStrategyAssistant
from app.services.deepseek_client import MOCK_PREFIX, DeepSeekClient
from app.services.llm_service import LLMService

BACKEND_APP = pathlib.Path(__file__).resolve().parent.parent / "app"

FORBIDDEN_PROVIDER_TOKENS = [
    "openai", "anthropic", "claude", "gemini", "mistral", "cohere", "ollama",
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
]


class TestDeepSeekOnly:
    def test_no_non_deepseek_env_vars_required(self):
        """The settings model must not reference any non-DeepSeek LLM provider."""
        field_names = set(Settings.model_fields.keys())
        for token in ("openai", "anthropic", "gemini", "mistral", "cohere", "ollama", "grok"):
            assert not any(token in f for f in field_names), f"forbidden provider field: {token}"
        assert "deepseek_api_key" in field_names

    def test_no_non_deepseek_providers_in_source(self):
        """No non-DeepSeek provider imports/SDKs/env vars anywhere in the backend."""
        for py_file in BACKEND_APP.rglob("*.py"):
            content = py_file.read_text().lower()
            for token in FORBIDDEN_PROVIDER_TOKENS:
                assert token.lower() not in content, f"{token} found in {py_file.name}"

    def test_missing_key_returns_mock_output(self):
        client = DeepSeekClient(api_key="")
        assert client.is_configured is False
        result = client.chat([{"role": "user", "content": "hello"}])
        assert result.is_mock is True
        assert result.text.startswith(MOCK_PREFIX)

    def test_placeholder_key_is_not_configured(self):
        assert DeepSeekClient(api_key="your_deepseek_api_key_here").is_configured is False

    def test_non_deepseek_model_rejected(self):
        with pytest.raises(ValueError):
            DeepSeekClient(api_key="x", model="gpt-4o")

    def test_status_never_contains_key(self):
        status = DeepSeekClient(api_key="secret-key-value").status()
        assert "secret-key-value" not in status.model_dump_json()
        assert status.provider == "deepseek"


class TestLLMServiceBoundary:
    def test_strategy_review_uses_deepseek_boundary(self):
        service = LLMService(client=DeepSeekClient(api_key=""))
        result = service.generate_strategy_review({"name": "Test", "strategy_type": "indicator"})
        assert result.provider == "deepseek"
        assert result.is_mock is True

    def test_run_analysis_uses_deepseek_boundary(self):
        service = LLMService(client=DeepSeekClient(api_key=""))
        result = service.generate_run_analysis({"current_equity": 100000, "trades": []})
        assert result.provider == "deepseek"
        assert result.is_mock is True

    def test_assistant_uses_deepseek_boundary(self):
        assistant = AIStrategyAssistant(llm=LLMService(client=DeepSeekClient(api_key="")))
        result = assistant.chat("How do I reduce drawdown?")
        assert result.provider == "deepseek"
        assert result.is_mock is True
