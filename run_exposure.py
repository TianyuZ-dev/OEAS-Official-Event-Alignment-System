#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from anas.config import Settings
from anas.env import load_api_keys
from anas.events.exposure_agents import ExposureExtractorAgent, ExposureJudgeAgent
from anas.events.schemas import ReadDocument
from anas.events.seed_loader import load_seed_events
from anas.events.storage import EventStore
from anas.progress import ProgressBar
from anas.providers import build_provider


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANAS official-event exposure extraction")
    parser.add_argument("--seed", default="data/seeds/official_events_seed_v1.json")
    parser.add_argument("--input", default="output/events/read_documents.jsonl")
    parser.add_argument("--output-dir", default="output/events")
    parser.add_argument("--provider", choices=["together", "fireworks", "gemini", "cerebras"], default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--event-id", action="append", default=None)
    parser.add_argument("--extractor-max-chars", type=int, default=12000)
    parser.add_argument("--judge-max-chars", type=int, default=6000)
    parser.add_argument("--force", action="store_true", help="Extract even if this event_id already exists in exposure_structs.jsonl")
    return parser.parse_args()


def main() -> int:
    load_api_keys()
    args = parse_args()
    settings = Settings()
    if args.provider:
        object.__setattr__(settings, "provider", args.provider)
    if args.model:
        object.__setattr__(settings, "model", args.model)

    seed_set = load_seed_events(args.seed)
    seed_by_id = {event.event_id: event for event in seed_set.events}
    documents = _latest_by_event_id(_load_read_documents(args.input))
    documents = [doc for doc in documents if doc.valid]
    if args.event_id:
        wanted = set(args.event_id)
        documents = [doc for doc in documents if doc.event_id in wanted]
    if args.limit is not None:
        documents = documents[: args.limit]

    print("ANAS exposure extraction")
    print(f"Provider: {settings.provider}")
    print(f"Model: {settings.model}")
    print(f"Documents selected: {len(documents)}")
    if not documents:
        print("No valid read documents found. Run `python3 run_events.py` first.")
        return 2

    provider = build_provider(settings)
    extractor = ExposureExtractorAgent(
        provider,
        max_chars=args.extractor_max_chars,
        delay_seconds=settings.llm_delay_seconds,
    )
    judge = ExposureJudgeAgent(
        provider,
        max_chars=args.judge_max_chars,
        delay_seconds=settings.llm_delay_seconds,
    )
    store = EventStore(args.output_dir)
    existing_exposure_ids = store.existing_event_ids(store.exposure_structs_file)
    skipped_existing = 0 if args.force else sum(1 for document in documents if document.event_id in existing_exposure_ids)
    pending_documents = documents if args.force else [
        document for document in documents if document.event_id not in existing_exposure_ids
    ]
    summary = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider.name,
        "model": provider.model,
        "input": args.input,
        "selected_count": len(documents),
        "pending_count": len(pending_documents),
        "skipped_existing": skipped_existing,
        "extracted": 0,
        "accepted": 0,
        "retry": 0,
        "rejected": 0,
        "errors": [],
    }
    if not pending_documents:
        print(f"Resume: all selected documents already extracted. skipped_existing={skipped_existing}")
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        store.write_exposure_summary(summary)
        print("Summary")
        print(summary)
        return 0

    processed = 0
    progress = ProgressBar(total=len(pending_documents), label="exposure")
    progress.update(processed, current="resume", extra=f"skipped_existing={skipped_existing}")

    for index, document in enumerate(pending_documents, 1):
        progress.update(processed, current=document.event_id)
        seed_event = seed_by_id.get(document.event_id)
        if seed_event is None:
            message = "missing seed metadata"
            progress.newline()
            print(f"[{index}/{len(pending_documents)}] {document.event_id}")
            print(f"  error: {message}")
            summary["errors"].append({"event_id": document.event_id, "error": message})
            processed += 1
            progress.update(processed, current=document.event_id, extra="error")
            continue

        try:
            exposure = extractor.extract(document=document, seed_event=seed_event)
            judgment = judge.judge(document=document, seed_event=seed_event, exposure=exposure)
        except Exception as exc:
            message = str(exc)
            progress.newline()
            print(f"[{index}/{len(pending_documents)}] {document.event_id}")
            print(f"  error: {message}")
            summary["errors"].append({"event_id": document.event_id, "error": message})
            processed += 1
            progress.update(processed, current=document.event_id, extra="error")
            continue

        store.append_exposure(exposure)
        store.append_judgment(judgment)
        existing_exposure_ids.add(document.event_id)
        processed += 1
        summary["extracted"] += 1
        if judgment.decision == "accept":
            summary["accepted"] += 1
        elif judgment.decision == "retry":
            summary["retry"] += 1
        else:
            summary["rejected"] += 1
        progress.update(
            processed,
            current=document.event_id,
            extra=f"{judgment.decision} score={judgment.score:.2f}",
        )

    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    store.write_exposure_summary(summary)
    progress.finish(
        message=(
            f"extracted={summary['extracted']} accepted={summary['accepted']} "
            f"retry={summary['retry']} rejected={summary['rejected']} errors={len(summary['errors'])}"
        )
    )
    print("Summary")
    print(summary)
    return 0 if not summary["errors"] else 1


def _load_read_documents(path: str | Path) -> list[ReadDocument]:
    read_path = Path(path)
    if not read_path.exists():
        return []
    documents = []
    skipped = 0
    for line_number, line in enumerate(read_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
            documents.append(ReadDocument.model_validate(payload))
        except Exception as exc:
            skipped += 1
            print(f"warning: skipped invalid read document line {read_path}:{line_number}: {exc}")
    if skipped:
        print(f"warning: skipped {skipped} invalid read document row(s) from {read_path}")
    return documents


def _latest_by_event_id(documents: list[ReadDocument]) -> list[ReadDocument]:
    latest: dict[str, ReadDocument] = {}
    for document in documents:
        latest[document.event_id] = document
    return list(latest.values())


if __name__ == "__main__":
    raise SystemExit(main())
