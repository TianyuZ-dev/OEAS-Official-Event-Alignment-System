#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DAILY_PATH = ROOT / "data/frictiongraph/daily_width_features_all.csv"
CHAIN_PATH = ROOT / "data/frictiongraph/chain_day_features_all.csv"
IMPACT_CASE_PATH = ROOT / "output/cases/jpy_stress_window_v1.csv"
RELEVANCE_CASE_PATH = ROOT / "output/cases/jpy_stress_window_relevance_v1.csv"
EXPOSURE_PATH = ROOT / "output/events_jpy_stress/accepted_exposures_latest.json"
OUTPUT_DIR = ROOT / "output/tableau_jpy_case"

FOCUS_START = date(2025, 11, 15)
FOCUS_END = date(2025, 12, 15)
FOCUS_DATES = {date(2025, 11, 28), date(2025, 12, 1)}


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    exposures = {row["event_id"]: row for row in json.loads(EXPOSURE_PATH.read_text(encoding="utf-8"))}

    _write_stress_daily()
    _write_top_chains()
    _write_case_events(exposures)
    _write_case_rankings(IMPACT_CASE_PATH, OUTPUT_DIR / "impact_case_ranking.csv", exposures, "impact")
    _write_case_rankings(RELEVANCE_CASE_PATH, OUTPUT_DIR / "relevance_case_ranking.csv", exposures, "relevance")
    _write_exposure_heatmaps(exposures)

    print("Wrote JPY Tableau case exports:")
    for path in sorted(OUTPUT_DIR.glob("*.csv")):
        print(f"- {path}")
    return 0


def _write_stress_daily() -> None:
    rows = []
    for row in _read_csv(DAILY_PATH):
        row_date = _parse_date(row["date"])
        if not FOCUS_START <= row_date <= FOCUS_END:
            continue
        rows.append(
            {
                "date": row["date"],
                "sum_rmsd": row.get("sum_rmsd", ""),
                "gap": row.get("gap", ""),
                "most_positive_chain_label": row.get("most_positive_chain_label", ""),
                "most_negative_chain_label": row.get("most_negative_chain_label", ""),
                "focus_day": "focus" if row_date in FOCUS_DATES else "context",
            }
        )
    _write_csv(OUTPUT_DIR / "jpy_stress_daily.csv", rows)


def _write_top_chains() -> None:
    by_date: dict[str, list[dict[str, str]]] = {}
    for row in _read_csv(CHAIN_PATH):
        row_date = _parse_date(row["date"])
        if row_date not in FOCUS_DATES:
            continue
        chain = row["chain"]
        by_date.setdefault(row["date"], []).append(
            {
                "date": row["date"],
                "chain": chain,
                "chain_short": chain.replace(" -> ", " > "),
                "contains_jpy": "yes" if "JPY" in chain.split(" -> ") else "no",
                "rmsd": row.get("rmsd", ""),
                "mean_friction": row.get("mean_friction", ""),
                "min_friction": row.get("min_friction", ""),
                "max_friction": row.get("max_friction", ""),
            }
        )

    rows = []
    for day, day_rows in sorted(by_date.items()):
        day_rows.sort(key=lambda item: float(item["rmsd"] or 0), reverse=True)
        for rank, row in enumerate(day_rows[:10], 1):
            row["rank"] = rank
            rows.append(row)
    _write_csv(OUTPUT_DIR / "jpy_top_chains_focus_days.csv", rows)


def _write_case_events(exposures: dict[str, dict[str, Any]]) -> None:
    rows = []
    for exposure in sorted(exposures.values(), key=lambda item: (item["event_date"], item["event_id"])):
        row_date = _parse_date(exposure["event_date"])
        if not FOCUS_START <= row_date <= FOCUS_END:
            continue
        rows.append(
            {
                "event_date": exposure["event_date"],
                "event_id": exposure["event_id"],
                "event_label": _event_label(exposure),
                "source": exposure["source"],
                "source_short": _source_short(exposure["source"]),
                "jpy_relevance": exposure["currency_relevance"].get("JPY", 0),
                "jpy_impact": exposure["currency_impact"].get("JPY", 0),
                "usd_relevance": exposure["currency_relevance"].get("USD", 0),
                "usd_impact": exposure["currency_impact"].get("USD", 0),
                "top_category": _top_key(exposure["category_relevance"]),
                "top_category_relevance": max(exposure["category_relevance"].values()),
                "rationale": exposure.get("rationale", ""),
            }
        )
    _write_csv(OUTPUT_DIR / "jpy_event_timeline.csv", rows)


def _write_case_rankings(source: Path, output: Path, exposures: dict[str, dict[str, Any]], mode: str) -> None:
    rows = _read_csv(source)
    rows.sort(key=lambda row: float(row["top_alignment_score"] or 0), reverse=True)
    selected = []
    for rank, row in enumerate(rows, 1):
        exposure = exposures.get(row["event_id"], {})
        selected.append(
            {
                "rank": rank,
                "mode": mode,
                "event_date": row["event_date"],
                "friction_date": row["friction_date"],
                "window": row["window"],
                "event_label": _event_label(exposure, fallback=row["title"]),
                "source_short": _source_short(row["source"]),
                "title": row["title"],
                "official_url": row["official_url"],
                "daily_sum_rmsd": row["daily_sum_rmsd"],
                "top_rmsd_chain": row["top_rmsd_chain"],
                "top_alignment_chain": row["top_alignment_chain"],
                "top_alignment_score": row["top_alignment_score"],
                "top_alignment_relevance_score": row["top_alignment_relevance_score"],
                "top_alignment_impact_score": row["top_alignment_impact_score"],
                "top_alignment_chain_rmsd_rank": row["top_alignment_chain_rmsd_rank"],
                "dominant_categories": row["dominant_categories"],
                "dominant_currencies": row["dominant_currencies"],
                "interpretation": row["interpretation"],
            }
        )
    _write_csv(output, selected)


def _write_exposure_heatmaps(exposures: dict[str, dict[str, Any]]) -> None:
    category_rows = []
    currency_rows = []
    for exposure in sorted(exposures.values(), key=lambda item: (item["event_date"], item["event_id"])):
        event_label = _event_label(exposure)
        for category, relevance in exposure["category_relevance"].items():
            impact = exposure["category_impact"].get(category, 0)
            if relevance or impact:
                category_rows.append(
                    {
                        "event_date": exposure["event_date"],
                        "event_label": event_label,
                        "source_short": _source_short(exposure["source"]),
                        "category": category,
                        "relevance": relevance,
                        "impact": impact,
                        "direction": exposure["category_direction"].get(category, 0),
                    }
                )
        for currency, relevance in exposure["currency_relevance"].items():
            impact = exposure["currency_impact"].get(currency, 0)
            if relevance or impact:
                currency_rows.append(
                    {
                        "event_date": exposure["event_date"],
                        "event_label": event_label,
                        "source_short": _source_short(exposure["source"]),
                        "currency": currency,
                        "relevance": relevance,
                        "impact": impact,
                        "direction": exposure["currency_direction"].get(currency, 0),
                    }
                )
    _write_csv(OUTPUT_DIR / "jpy_category_exposure_heatmap.csv", category_rows)
    _write_csv(OUTPUT_DIR / "jpy_currency_exposure_heatmap.csv", currency_rows)


def _event_label(exposure: dict[str, Any], fallback: str = "") -> str:
    if not exposure:
        return fallback
    title = fallback or exposure.get("rationale", "")[:0] or exposure.get("event_id", "")
    title = _title_from_event_id(exposure.get("event_id", "")) if not fallback else fallback
    source = _source_short(exposure.get("source", ""))
    return f"{exposure.get('event_date', '')} | {source} | {title}"


def _title_from_event_id(event_id: str) -> str:
    known = {
        "boj_2025_11_27_noguchi_oita_speech": "BOJ Noguchi Speech",
        "boj_2025_12_01_ueda_nagoya_speech": "BOJ Ueda Speech",
        "mof_2025_11_28_fx_intervention_operations": "MOF FX Intervention",
        "mof_2025_11_28_jgb_issuance_plan_revision": "MOF JGB Issuance",
        "fed_2025_12_10_fomc_statement": "Fed FOMC Statement",
        "mof_2025_12_05_international_reserves": "MOF International Reserves",
    }
    if event_id in known:
        return known[event_id]
    return event_id.split("_", 4)[-1].replace("_", " ").title()


def _source_short(source: str) -> str:
    aliases = {
        "Bank of Japan": "BOJ",
        "Japan Ministry of Finance": "MOF Japan",
        "Cabinet Office Japan": "CAO Japan",
        "Federal Reserve Board": "Fed",
    }
    return aliases.get(source, source)


def _top_key(values: dict[str, int]) -> str:
    return max(values.items(), key=lambda item: item[1])[0] if values else ""


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


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
