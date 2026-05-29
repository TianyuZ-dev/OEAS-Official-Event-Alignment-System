from __future__ import annotations

from anas.config import Settings
from anas.providers.base import LLMProvider
from anas.providers.gemini import GeminiProvider
from anas.providers.openai_compatible import OpenAICompatibleProvider


DEFAULT_MODELS = {
    "together": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "fireworks": "accounts/fireworks/models/openai-gpt-oss-120b",
    "cerebras": "llama-3.3-70b",
    "gemini": "gemini-2.5-flash-lite",
}


def build_provider(settings: Settings) -> LLMProvider:
    provider = settings.provider.lower().strip()
    model = settings.model or DEFAULT_MODELS.get(provider, "")

    if provider == "together":
        return OpenAICompatibleProvider(
            name="together",
            base_url="https://api.together.xyz/v1",
            api_key_env="TOGETHER_API_KEY",
            model=model or DEFAULT_MODELS["together"],
        )
    if provider == "fireworks":
        return OpenAICompatibleProvider(
            name="fireworks",
            base_url="https://api.fireworks.ai/inference/v1",
            api_key_env="FIREWORKS_API_KEY",
            model=model or DEFAULT_MODELS["fireworks"],
        )
    if provider == "cerebras":
        return OpenAICompatibleProvider(
            name="cerebras",
            base_url="https://api.cerebras.ai/v1",
            api_key_env="CEREBRAS_API_KEY",
            model=model or DEFAULT_MODELS["cerebras"],
        )
    if provider == "gemini":
        return GeminiProvider(model=model or DEFAULT_MODELS["gemini"], timeout=settings.request_timeout)

    raise ValueError(f"Unknown provider: {settings.provider}")

