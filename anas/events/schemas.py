from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from anas.events.taxonomy import CATEGORIES, EVENT_CURRENCIES, HORIZONS


class SeedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_date: str
    source_policy_id: str
    source: str
    document_type: str
    title: str
    source_url: str
    primary_categories: list[str]
    country_focus: list[str]
    currency_focus: list[str]
    alignment_note: str

    @field_validator("primary_categories")
    @classmethod
    def validate_categories(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - set(CATEGORIES))
        if unknown:
            raise ValueError(f"Unknown categories: {unknown}")
        return values

    @field_validator("currency_focus")
    @classmethod
    def validate_currencies(cls, values: list[str]) -> list[str]:
        unknown = sorted(set(values) - set(EVENT_CURRENCIES))
        if unknown:
            raise ValueError(f"Unknown currencies/proxies: {unknown}")
        return values


class SeedEventSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    generated_at: str
    source_document: str
    frictiongraph_alignment_space: dict
    events: list[SeedEvent]

    @model_validator(mode="after")
    def validate_unique_events(self) -> "SeedEventSet":
        ids = [event.event_id for event in self.events]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate event_id in seed set")
        return self


class RawDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_date: str
    source_policy_id: str
    source: str
    document_type: str
    title: str
    source_url: str
    fetched_at: str
    http_status: int
    final_url: str
    raw_html: str
    raw_text: str


class ReadDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_date: str
    source_policy_id: str
    source: str
    document_type: str
    title: str
    source_url: str
    final_url: str
    fetched_at: str
    content_sha256: str
    text_sha256: str
    text_chars: int
    word_count: int
    valid: bool
    reason: str
    text_clean: str


class ExposureStruct(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    event_date: str
    source: str
    document_type: str
    category_relevance: dict[str, int] = Field(default_factory=dict)
    category_score: dict[str, int]
    category_direction: dict[str, int]
    category_impact: dict[str, int]
    country_relevance: dict[str, int] = Field(default_factory=dict)
    country_score: dict[str, int]
    country_direction: dict[str, int]
    country_impact: dict[str, int]
    currency_relevance: dict[str, int] = Field(default_factory=dict)
    currency_score: dict[str, int]
    currency_direction: dict[str, int]
    currency_impact: dict[str, int]
    horizon: dict[str, int]
    rationale: str = Field(default="", max_length=1000)

    @field_validator("category_score", "category_impact")
    @classmethod
    def validate_category_positive(cls, values: dict[str, int]) -> dict[str, int]:
        return _clamp_dict(values, CATEGORIES, 0, 100)

    @field_validator("category_relevance")
    @classmethod
    def validate_category_relevance(cls, values: dict[str, int]) -> dict[str, int]:
        if not values:
            return {}
        return _clamp_dict(values, CATEGORIES, 0, 100)

    @field_validator("category_direction")
    @classmethod
    def validate_category_direction(cls, values: dict[str, int]) -> dict[str, int]:
        return _clamp_dict(values, CATEGORIES, -100, 100)

    @field_validator("currency_score", "currency_impact")
    @classmethod
    def validate_currency_positive(cls, values: dict[str, int]) -> dict[str, int]:
        return _clamp_dict(values, EVENT_CURRENCIES, 0, 100)

    @field_validator("currency_relevance")
    @classmethod
    def validate_currency_relevance(cls, values: dict[str, int]) -> dict[str, int]:
        if not values:
            return {}
        return _clamp_dict(values, EVENT_CURRENCIES, 0, 100)

    @field_validator("currency_direction")
    @classmethod
    def validate_currency_direction(cls, values: dict[str, int]) -> dict[str, int]:
        return _clamp_dict(values, EVENT_CURRENCIES, -100, 100)

    @field_validator("horizon")
    @classmethod
    def validate_horizon(cls, values: dict[str, int]) -> dict[str, int]:
        return _clamp_dict(values, HORIZONS, 0, 100)

    @model_validator(mode="after")
    def enforce_zero_discipline(self) -> "ExposureStruct":
        if not self.category_relevance:
            self.category_relevance = dict(self.category_score)
        else:
            self.category_score = dict(self.category_relevance)

        if not self.country_relevance:
            self.country_relevance = dict(self.country_score)
        else:
            self.country_score = dict(self.country_relevance)

        if not self.currency_relevance:
            self.currency_relevance = dict(self.currency_score)
        else:
            self.currency_score = dict(self.currency_relevance)

        for category, relevance in self.category_relevance.items():
            if relevance < 20:
                self.category_direction[category] = 0
                self.category_impact[category] = 0
        for currency, relevance in self.currency_relevance.items():
            if relevance < 20:
                self.currency_direction[currency] = 0
                self.currency_impact[currency] = 0
        return self


class ExposureJudgment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    score: float = Field(ge=0.0, le=1.0)
    decision: Literal["accept", "retry", "reject"]
    reason: str


def empty_exposure_dict(keys: list[str], value: int = 0) -> dict[str, int]:
    return {key: value for key in keys}


def _clamp_dict(values: dict[str, int], keys: list[str], low: int, high: int) -> dict[str, int]:
    unknown = sorted(set(values) - set(keys))
    if unknown:
        raise ValueError(f"Unknown keys: {unknown}")
    return {key: max(low, min(high, int(values.get(key, 0)))) for key in keys}
