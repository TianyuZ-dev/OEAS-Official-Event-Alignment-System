from __future__ import annotations

import json
import os

import requests

from anas.providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, *, model: str, timeout: int = 45):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to .env or export it.")
        self.name = "gemini"
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema: dict,
        schema_name: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "responseMimeType": "application/json",
                "responseSchema": schema,
            },
        }
        response = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(part.get("text", "") for part in parts) or "{}"

