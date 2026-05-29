from __future__ import annotations

import hashlib
import re

from anas.events.schemas import RawDocument, ReadDocument


class DocumentReader:
    """Validate, normalize, and fingerprint official documents."""

    def __init__(self, *, min_words: int = 80):
        self.min_words = min_words

    def read(self, raw: RawDocument) -> ReadDocument:
        text = normalize_text(raw.raw_text)
        words = text.split()
        valid = True
        reason = f"ok:{len(words)}"
        if len(words) < self.min_words:
            valid = False
            reason = f"too_short:{len(words)}"

        return ReadDocument(
            event_id=raw.event_id,
            event_date=raw.event_date,
            source_policy_id=raw.source_policy_id,
            source=raw.source,
            document_type=raw.document_type,
            title=raw.title,
            source_url=raw.source_url,
            final_url=raw.final_url,
            fetched_at=raw.fetched_at,
            content_sha256=sha256_text(raw.raw_html),
            text_sha256=sha256_text(text),
            text_chars=len(text),
            word_count=len(words),
            valid=valid,
            reason=reason,
            text_clean=text,
        )


def normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

