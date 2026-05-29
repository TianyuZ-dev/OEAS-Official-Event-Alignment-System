from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class EventStore:
    def __init__(self, output_dir: str | Path = "output/events"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.raw_documents_file = self.output_dir / "raw_documents.jsonl"
        self.read_documents_file = self.output_dir / "read_documents.jsonl"
        self.exposure_structs_file = self.output_dir / "exposure_structs.jsonl"
        self.exposure_judgments_file = self.output_dir / "exposure_judgments.jsonl"
        self.fetch_summary_file = self.output_dir / "fetch_summary.json"
        self.exposure_summary_file = self.output_dir / "exposure_summary.json"

    def append_raw(self, record: BaseModel) -> None:
        self._append_jsonl(self.raw_documents_file, record.model_dump())

    def append_read(self, record: BaseModel) -> None:
        self._append_jsonl(self.read_documents_file, record.model_dump())

    def append_exposure(self, record: BaseModel) -> None:
        self._append_jsonl(self.exposure_structs_file, record.model_dump())

    def append_judgment(self, record: BaseModel) -> None:
        self._append_jsonl(self.exposure_judgments_file, record.model_dump())

    def existing_event_ids(self, path: Path) -> set[str]:
        if not path.exists():
            return set()
        ids = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            event_id = record.get("event_id")
            if event_id:
                ids.add(str(event_id))
        return ids

    def write_summary(self, summary: dict[str, Any]) -> None:
        self.fetch_summary_file.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    def write_exposure_summary(self, summary: dict[str, Any]) -> None:
        self.exposure_summary_file.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
