from __future__ import annotations

import json
import time
from typing import Any

from anas.events.llm_json import loads_json_object
from anas.events.schemas import ExposureJudgment, ExposureStruct, ReadDocument, SeedEvent
from anas.events.taxonomy import CATEGORIES, EVENT_CURRENCIES, HORIZONS
from anas.providers.base import LLMProvider


EXPOSURE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "event_date": {"type": "string"},
        "source": {"type": "string"},
        "document_type": {"type": "string"},
        "category_relevance": {"type": "object", "additionalProperties": {"type": "integer"}},
        "category_score": {"type": "object", "additionalProperties": {"type": "integer"}},
        "category_direction": {"type": "object", "additionalProperties": {"type": "integer"}},
        "category_impact": {"type": "object", "additionalProperties": {"type": "integer"}},
        "country_relevance": {"type": "object", "additionalProperties": {"type": "integer"}},
        "country_score": {"type": "object", "additionalProperties": {"type": "integer"}},
        "country_direction": {"type": "object", "additionalProperties": {"type": "integer"}},
        "country_impact": {"type": "object", "additionalProperties": {"type": "integer"}},
        "currency_relevance": {"type": "object", "additionalProperties": {"type": "integer"}},
        "currency_score": {"type": "object", "additionalProperties": {"type": "integer"}},
        "currency_direction": {"type": "object", "additionalProperties": {"type": "integer"}},
        "currency_impact": {"type": "object", "additionalProperties": {"type": "integer"}},
        "horizon": {"type": "object", "additionalProperties": {"type": "integer"}},
        "rationale": {"type": "string"},
    },
    "required": [
        "event_id",
        "event_date",
        "source",
        "document_type",
        "category_relevance",
        "category_score",
        "category_direction",
        "category_impact",
        "country_relevance",
        "country_score",
        "country_direction",
        "country_impact",
        "currency_relevance",
        "currency_score",
        "currency_direction",
        "currency_impact",
        "horizon",
        "rationale",
    ],
    "additionalProperties": False,
}

JUDGMENT_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "event_id": {"type": "string"},
        "score": {"type": "number", "minimum": 0, "maximum": 1},
        "decision": {"type": "string", "enum": ["accept", "retry", "reject"]},
        "reason": {"type": "string"},
    },
    "required": ["event_id", "score", "decision", "reason"],
    "additionalProperties": False,
}

EXTRACTOR_SYSTEM = """You are ANAS Exposure Extractor.

Your skill is to convert one official geopolitical/economic event document into
a strict exposure struct for FrictionGraph alignment.

You must only use evidence from the official document and the supplied event metadata.
Do not use copyrighted news context. Do not predict markets.

Category keys are fixed:
{categories}

Currency/proxy keys are fixed:
{currencies}

Horizon keys are fixed:
{horizons}

Scoring:
- relevance: 0-100 official-document relevance/exposure. This can be high even when the document reports a neutral result.
- score: same value as relevance. This is kept for backward compatibility.
- direction: -100 to 100. Positive means supportive/strengthening/risk-on for that dimension; negative means adverse/weakening/risk-off.
- impact: 0-100 realized or expected strength of event shock / market-structure attention. A highly relevant neutral disclosure can have impact 0.
- If relevance < 20, direction and impact must be 0.
- Prefer zero over speculative weak exposure.

Important distinction:
- A foreign-exchange intervention disclosure with amount 0 can have currency_relevance["JPY"] = 100 but currency_impact["JPY"] = 0.
- A central-bank speech that changes or strongly frames policy expectations can have high relevance and nonzero impact.

Return exactly one JSON object matching the schema. No markdown.
"""

EXTRACTOR_USER = """Event metadata:
{event_metadata}

Official document:
{document_text}
"""

JUDGE_SYSTEM = """You are ANAS Exposure Judge.

Your skill is quality control. Given an official document and an extracted
exposure struct, decide whether the struct is useful for ANAS's 10-event demo.

Reject or retry if:
- categories are unsupported by the official document
- currency/proxy exposure is overextended or speculative
- the struct uses unsupported currencies
- score/direction/impact violate zero discipline
- the rationale claims prediction or causality

Return exactly one JSON object:
{"event_id": "...", "score": 0.0-1.0, "decision": "accept|retry|reject", "reason": "one sentence"}
"""

JUDGE_USER = """Event metadata:
{event_metadata}

Official document excerpt:
{document_text}

Extracted exposure struct:
{struct}
"""


class ExposureExtractorAgent:
    def __init__(self, provider: LLMProvider, *, max_chars: int = 12000, delay_seconds: float = 0.2):
        self.provider = provider
        self.max_chars = max_chars
        self.delay_seconds = delay_seconds

    def extract(self, *, document: ReadDocument, seed_event: SeedEvent) -> ExposureStruct:
        event_metadata = _event_metadata(seed_event)
        raw = self.provider.complete_json(
            system=EXTRACTOR_SYSTEM.format(
                categories=", ".join(CATEGORIES),
                currencies=", ".join(EVENT_CURRENCIES),
                horizons=", ".join(HORIZONS),
            ),
            user=EXTRACTOR_USER.format(
                event_metadata=json.dumps(event_metadata, ensure_ascii=False, indent=2),
                document_text=document.text_clean[: self.max_chars],
            ),
            schema=EXPOSURE_JSON_SCHEMA,
            schema_name="AnasExposureStruct",
            max_tokens=1600,
            temperature=0.0,
        )
        time.sleep(self.delay_seconds)
        obj = loads_json_object(raw)
        obj.setdefault("event_id", document.event_id)
        obj.setdefault("event_date", document.event_date)
        obj.setdefault("source", document.source)
        obj.setdefault("document_type", document.document_type)
        obj.setdefault("rationale", "")
        if isinstance(obj["rationale"], str):
            obj["rationale"] = obj["rationale"][:1000]
        _fill_relevance_compatibility(obj)
        _normalize_keyed_scores(obj)
        return ExposureStruct.model_validate(obj)


class ExposureJudgeAgent:
    def __init__(self, provider: LLMProvider, *, max_chars: int = 6000, delay_seconds: float = 0.2):
        self.provider = provider
        self.max_chars = max_chars
        self.delay_seconds = delay_seconds

    def judge(
        self,
        *,
        document: ReadDocument,
        seed_event: SeedEvent,
        exposure: ExposureStruct,
    ) -> ExposureJudgment:
        raw = self.provider.complete_json(
            system=JUDGE_SYSTEM,
            user=JUDGE_USER.format(
                event_metadata=json.dumps(_event_metadata(seed_event), ensure_ascii=False, indent=2),
                document_text=document.text_clean[: self.max_chars],
                struct=exposure.model_dump_json(indent=2),
            ),
            schema=JUDGMENT_JSON_SCHEMA,
            schema_name="AnasExposureJudgment",
            max_tokens=300,
            temperature=0.0,
        )
        time.sleep(self.delay_seconds)
        obj = loads_json_object(raw)
        obj.setdefault("event_id", document.event_id)
        return ExposureJudgment.model_validate(obj)


def _event_metadata(seed_event: SeedEvent) -> dict[str, Any]:
    return {
        "event_id": seed_event.event_id,
        "event_date": seed_event.event_date,
        "source_policy_id": seed_event.source_policy_id,
        "source": seed_event.source,
        "document_type": seed_event.document_type,
        "title": seed_event.title,
        "source_url": seed_event.source_url,
        "primary_categories_hint": seed_event.primary_categories,
        "country_focus_hint": seed_event.country_focus,
        "currency_focus_hint": seed_event.currency_focus,
        "alignment_note": seed_event.alignment_note,
    }


def _fill_relevance_compatibility(obj: dict[str, Any]) -> None:
    for prefix in ("category", "country", "currency"):
        relevance_key = f"{prefix}_relevance"
        score_key = f"{prefix}_score"
        if relevance_key not in obj and score_key in obj:
            obj[relevance_key] = obj[score_key]
        if score_key not in obj and relevance_key in obj:
            obj[score_key] = obj[relevance_key]


def _normalize_keyed_scores(obj: dict[str, Any]) -> None:
    key_sets = {
        "category": set(CATEGORIES),
        "currency": set(EVENT_CURRENCIES),
        "horizon": set(HORIZONS),
    }
    for prefix, allowed_keys in key_sets.items():
        suffixes = ("relevance", "score", "direction", "impact") if prefix != "horizon" else ("",)
        for suffix in suffixes:
            key = prefix if not suffix else f"{prefix}_{suffix}"
            values = obj.get(key)
            if not isinstance(values, dict):
                continue
            obj[key] = {name: value for name, value in values.items() if name in allowed_keys}
