#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export latest clean ANAS event records")
    parser.add_argument("--events-dir", default="output/events")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    events_dir = Path(args.events_dir)
    events_dir.mkdir(parents=True, exist_ok=True)

    read_documents = _latest_by_event_id(_load_jsonl(events_dir / "read_documents.jsonl"))
    exposures = _latest_by_event_id(_load_jsonl(events_dir / "exposure_structs.jsonl"))
    judgments = _latest_by_event_id(_load_jsonl(events_dir / "exposure_judgments.jsonl"))

    accepted = []
    for event_id, exposure in exposures.items():
        judgment = judgments.get(event_id)
        if not judgment or judgment.get("decision") != "accept":
            continue
        accepted.append(
            {
                **exposure,
                "judgment_score": judgment.get("score"),
                "judgment_reason": judgment.get("reason", ""),
            }
        )

    read_list = sorted(read_documents.values(), key=lambda row: (row.get("event_date", ""), row.get("event_id", "")))
    accepted_list = sorted(accepted, key=lambda row: (row.get("event_date", ""), row.get("event_id", "")))
    judgment_list = sorted(judgments.values(), key=lambda row: row.get("event_id", ""))

    _write_json(events_dir / "read_documents_latest.json", read_list)
    _write_json(events_dir / "accepted_exposures_latest.json", accepted_list)
    _write_json(events_dir / "exposure_judgments_latest.json", judgment_list)

    print("ANAS latest event export")
    print(f"Read documents: {len(read_list)}")
    print(f"Accepted exposures: {len(accepted_list)}")
    print(f"Latest judgments: {len(judgment_list)}")
    print(f"Wrote: {events_dir / 'accepted_exposures_latest.json'}")
    return 0


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    skipped = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            skipped += 1
            print(f"warning: skipped invalid JSONL row {path}:{line_number}: {exc}")
            continue
        if isinstance(row, dict):
            rows.append(row)
    if skipped:
        print(f"warning: skipped {skipped} invalid JSONL row(s) from {path}")
    return rows


def _latest_by_event_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest = {}
    for row in rows:
        event_id = row.get("event_id")
        if event_id:
            latest[str(event_id)] = row
    return latest


def _write_json(path: Path, records: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
