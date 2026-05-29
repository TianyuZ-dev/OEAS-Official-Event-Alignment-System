#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone

from anas.events.reader import DocumentReader
from anas.events.scout import OfficialSourceScout
from anas.events.seed_loader import load_seed_events
from anas.events.storage import EventStore
from anas.progress import ProgressBar


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ANAS official-event ingestion pipeline")
    parser.add_argument("--seed", default="data/seeds/official_events_seed_v1.json")
    parser.add_argument("--output-dir", default="output/events")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--event-id", action="append", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Validate seed records without network fetch")
    parser.add_argument("--min-words", type=int, default=80)
    parser.add_argument("--force", action="store_true", help="Fetch even if this event_id already exists in read_documents.jsonl")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seed_set = load_seed_events(args.seed)
    events = seed_set.events
    if args.event_id:
        wanted = set(args.event_id)
        events = [event for event in events if event.event_id in wanted]
    if args.limit is not None:
        events = events[: args.limit]

    print(f"ANAS official-event pipeline")
    print(f"Seed: {args.seed}")
    print(f"Events selected: {len(events)} / {len(seed_set.events)}")
    print(f"Dry run: {args.dry_run}")

    if args.dry_run:
        for event in events:
            print(f"- {event.event_date} {event.event_id} | {event.source}")
        return 0

    scout = OfficialSourceScout()
    reader = DocumentReader(min_words=args.min_words)
    store = EventStore(args.output_dir)
    existing_read_ids = store.existing_event_ids(store.read_documents_file)
    skipped_existing = 0 if args.force else sum(1 for event in events if event.event_id in existing_read_ids)
    pending_events = events if args.force else [event for event in events if event.event_id not in existing_read_ids]
    summary = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed,
        "output_dir": args.output_dir,
        "selected_count": len(events),
        "pending_count": len(pending_events),
        "skipped_existing": skipped_existing,
        "fetched": 0,
        "valid": 0,
        "invalid": 0,
        "errors": [],
    }
    if not pending_events:
        print(f"Resume: all selected events already fetched. skipped_existing={skipped_existing}")
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        store.write_summary(summary)
        print("Summary")
        print(summary)
        return 0

    processed = 0
    progress = ProgressBar(total=len(pending_events), label="fetch")
    progress.update(processed, current="resume", extra=f"skipped_existing={skipped_existing}")

    for index, event in enumerate(pending_events, 1):
        progress.update(processed, current=event.event_id)
        try:
            raw = scout.fetch(event)
            read = reader.read(raw)
        except Exception as exc:
            message = str(exc)
            progress.newline()
            print(f"[{index}/{len(pending_events)}] {event.event_id}")
            print(f"  error: {message}")
            summary["errors"].append({"event_id": event.event_id, "error": message})
            processed += 1
            progress.update(processed, current=event.event_id, extra="error")
            continue

        store.append_raw(raw)
        store.append_read(read)
        existing_read_ids.add(event.event_id)
        processed += 1
        summary["fetched"] += 1
        if read.valid:
            summary["valid"] += 1
        else:
            summary["invalid"] += 1
        progress.update(
            processed,
            current=event.event_id,
            extra=f"status={raw.http_status} words={read.word_count} valid={read.valid}",
        )

    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    store.write_summary(summary)
    progress.finish(message=f"fetched={summary['fetched']} valid={summary['valid']} errors={len(summary['errors'])}")
    print("Summary")
    print(summary)
    return 0 if not summary["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
