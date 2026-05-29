from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
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
        """Return a raw JSON string from the provider."""

