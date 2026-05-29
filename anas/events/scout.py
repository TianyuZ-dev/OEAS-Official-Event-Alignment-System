from __future__ import annotations

from datetime import datetime, timezone

import requests

from anas.events.connectors import connector_for_event
from anas.events.schemas import RawDocument, SeedEvent


class OfficialSourceScout:
    """Fetch official event pages from the seed set."""

    def __init__(self, *, timeout: int = 45):
        self.timeout = timeout

    def fetch(self, event: SeedEvent) -> RawDocument:
        try:
            result = connector_for_event(event, timeout=self.timeout).fetch(event)
        except requests.RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", "network")
            raise RuntimeError(f"Official source request failed for event_id={event.event_id}, status={status}") from None
        except RuntimeError:
            raise

        return RawDocument(
            event_id=event.event_id,
            event_date=event.event_date,
            source_policy_id=event.source_policy_id,
            source=event.source,
            document_type=event.document_type,
            title=event.title,
            source_url=event.source_url,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            http_status=result.http_status,
            final_url=result.final_url,
            raw_html=result.raw_html,
            raw_text=result.raw_text,
        )
