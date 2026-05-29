#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "data/seeds/general_events_2024_2025_seed_v1.json"
IMPACT_DIR = ROOT / "output/alignment_general_2024_2025"
RELEVANCE_DIR = ROOT / "output/alignment_general_2024_2025_relevance"
OUTPUT_DIR = ROOT / "output/tableau_general_2024_2025"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seed_events = _load_seed_events()

    _write_ranking(
        source=IMPACT_DIR / "event_alignment_summary.csv",
        output=OUTPUT_DIR / "impact_ranking_top20.csv",
        seed_events=seed_events,
        mode="impact",
    )
    _write_ranking(
        source=RELEVANCE_DIR / "event_alignment_summary.csv",
        output=OUTPUT_DIR / "relevance_ranking_top20.csv",
        seed_events=seed_events,
        mode="relevance",
    )
    _write_nonzero_waterfall(
        source=IMPACT_DIR / "waterfall_category_daily.csv",
        output=OUTPUT_DIR / "category_waterfall_nonzero.csv",
        dimension_name="category",
    )
    _write_nonzero_waterfall(
        source=IMPACT_DIR / "waterfall_currency_daily.csv",
        output=OUTPUT_DIR / "currency_waterfall_nonzero.csv",
        dimension_name="currency",
    )

    print("Wrote Tableau-friendly exports:")
    for path in sorted(OUTPUT_DIR.glob("*.csv")):
        print(f"- {path}")
    return 0


def _load_seed_events() -> dict[str, dict[str, Any]]:
    payload = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    return {event["event_id"]: event for event in payload["events"]}


def _write_ranking(source: Path, output: Path, seed_events: dict[str, dict[str, Any]], mode: str) -> None:
    rows = _read_csv(source)
    rows = [row for row in rows if row["window"] == "3_day"]
    rows.sort(key=lambda row: float(row["top_alignment_score"] or 0), reverse=True)

    selected = []
    seen: set[str] = set()
    for row in rows:
        event_id = row["event_id"]
        if event_id in seen:
            continue
        seen.add(event_id)
        event = seed_events.get(event_id, {})
        source = event.get("source", "")
        source_short = _source_short(source)
        selected.append(
            {
                "rank": len(selected) + 1,
                "mode": mode,
                "event_date": row["event_date"],
                "friction_date": row["friction_date"],
                "event_axis_label": _event_axis_label(row, event, len(selected) + 1),
                "event_label": _event_label(row, event),
                "event_id": event_id,
                "source": source,
                "source_short": source_short,
                "title": event.get("title", ""),
                "top_alignment_score": row["top_alignment_score"],
                "top_alignment_chain": row["top_alignment_chain"],
                "top_alignment_chain_rmsd": row["top_alignment_chain_rmsd"],
                "top_alignment_currency_overlap": row["top_alignment_currency_overlap"],
                "top_alignment_relevance_score": row["top_alignment_relevance_score"],
                "top_alignment_impact_score": row["top_alignment_impact_score"],
            }
        )
        if len(selected) >= 20:
            break
    _write_csv(output, selected)


def _write_nonzero_waterfall(source: Path, output: Path, dimension_name: str) -> None:
    rows = _read_csv(source)
    selected = []
    for row in rows:
        score = float(row["score"] or 0)
        impact = float(row["impact"] or 0)
        direction = float(row["direction"] or 0)
        if score == 0 and impact == 0 and direction == 0:
            continue
        selected.append(
            {
                "date": row["date"],
                dimension_name: row[dimension_name],
                "score": row["score"],
                "impact": row["impact"],
                "direction": row["direction"],
                "abs_direction": abs(direction),
            }
        )
    _write_csv(output, selected)


def _event_label(row: dict[str, str], event: dict[str, Any]) -> str:
    source = _source_short(event.get("source", ""))
    title = event.get("title") or row["event_id"]
    title = " ".join(title.split())
    if len(title) > 72:
        title = title[:69].rstrip() + "..."
    return f"{row['event_date']} | {source} | {title}"


def _event_axis_label(row: dict[str, str], event: dict[str, Any], rank: int) -> str:
    source = _source_short(event.get("source", ""))
    title = event.get("title") or row["event_id"]
    topic = _topic_short(title)
    return f"{rank:02d} | {row['event_date']} | {source} | {topic}"


def _source_short(source: str) -> str:
    aliases = {
        "Federal Reserve Board": "Fed",
        "Office of the U.S. Trade Representative": "USTR",
        "U.S. Treasury / OFAC": "Treasury/OFAC",
        "White House": "White House",
    }
    return aliases.get(source, source)


def _topic_short(title: str) -> str:
    title_l = title.lower()
    topics = [
        ("sanction", "Sanctions"),
        ("tariff", "Tariffs"),
        ("section 301", "Section 301"),
        ("federal open market committee", "FOMC"),
        ("discount rate", "Discount Rate"),
        ("bank term funding", "BTFP"),
        ("financial stability", "Financial Stability"),
        ("treasury international capital", "TIC Data"),
        ("chips", "CHIPS"),
        ("semiconductor", "Semiconductors"),
        ("energy", "Energy"),
        ("inflation", "Inflation"),
        ("consumer price index", "CPI"),
        ("g20", "G20"),
        ("china", "China"),
        ("taiwan", "Taiwan"),
        ("japan", "Japan"),
        ("korea", "Korea"),
        ("russia", "Russia"),
        ("iran", "Iran"),
        ("houthi", "Houthis"),
        ("maduro", "Maduro"),
        ("cartel", "Cartel"),
        ("trade", "Trade"),
        ("tax", "Tax"),
    ]
    for needle, label in topics:
        if needle in title_l:
            return label
    words = [word.strip(" ,:;()[]") for word in title.split()]
    words = [word for word in words if word]
    fallback = " ".join(words[:4])
    return fallback[:32]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    raise SystemExit(main())
