from __future__ import annotations

import os

from openai import OpenAI

from anas.providers.base import LLMProvider


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, *, name: str, base_url: str, api_key_env: str, model: str):
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise RuntimeError(f"{api_key_env} is not set. Add it to .env or export it.")
        self.name = name
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

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
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": schema,
                "strict": True,
            },
        }
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format=response_format,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as exc:
            # Some OpenAI-compatible providers support json_object but not strict schema for every model.
            if "response_format" not in str(exc) and "json_schema" not in str(exc):
                raise
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user + "\n\nReturn only one valid JSON object matching the requested schema."},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens,
            )
        return response.choices[0].message.content or "{}"

