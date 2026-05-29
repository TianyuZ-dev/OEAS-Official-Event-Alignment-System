from __future__ import annotations

import json
from pathlib import Path

from anas.events.schemas import SeedEventSet


def load_seed_events(path: str | Path = "data/seeds/official_events_seed_v1.json") -> SeedEventSet:
    seed_path = Path(path)
    payload = json.loads(seed_path.read_text(encoding="utf-8"))
    return SeedEventSet.model_validate(payload)

