#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from anas.events.taxonomy import CATEGORIES, EVENT_CURRENCIES


WINDOWS = ["same_day", "next_day", "3_day", "7_day"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Align ANAS official events with FrictionGraph daily chain outputs")
    parser.add_argument("--exposures", default="output/events/accepted_exposures_latest.json")
    parser.add_argument("--ranking-mode", choices=["impact", "relevance"], default="impact")
    parser.add_argument(
        "--friction-daily",
        default="data/frictiongraph/daily_width_features_all.csv",
    )
    parser.add_argument(
        "--friction-chain",
        default="data/frictiongraph/chain_day_features_all.csv",
    )
    parser.add_argument("--output-dir", default="output/alignment")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exposures = _load_json(args.exposures)
    if not exposures:
        print("No accepted exposure records found. Run `python3 run_event_latest.py` first.")
        return 2

    daily_rows = _load_daily_rows(args.friction_daily)
    chain_rows_by_date = _load_chain_rows(args.friction_chain)
    if not daily_rows or not chain_rows_by_date:
        print("Missing FrictionGraph processed rows.")
        return 2

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    daily_by_date = {row["date"]: row for row in daily_rows}
    available_dates = sorted(daily_by_date)

    summary_rows = []
    chain_alignment_rows = []
    for exposure in sorted(exposures, key=lambda row: (row.get("event_date", ""), row.get("event_id", ""))):
        event_date = _parse_date(exposure["event_date"])
        for window in WINDOWS:
            selected_date = _select_window_date(event_date, window, daily_by_date, available_dates)
            if selected_date is None:
                continue

            daily = daily_by_date[selected_date]
            chain_rows = chain_rows_by_date.get(selected_date, [])
            if not chain_rows:
                continue

            rows_for_event = [
                _score_chain(exposure, daily, chain_row, window, ranking_mode=args.ranking_mode)
                for chain_row in chain_rows
            ]
            _assign_rank(rows_for_event, "chain_rmsd", "chain_rank_by_rmsd")
            _assign_rank(rows_for_event, "alignment_score", "chain_rank_by_alignment")
            _assign_rank(rows_for_event, "relevance_alignment_score", "chain_rank_by_relevance_alignment")
            _assign_rank(rows_for_event, "impact_alignment_score", "chain_rank_by_impact_alignment")
            rows_for_event.sort(key=lambda row: (row["chain_rank_by_alignment"], row["chain_rank_by_rmsd"]))
            chain_alignment_rows.extend(rows_for_event)

            top_rmsd = min(rows_for_event, key=lambda row: row["chain_rank_by_rmsd"])
            top_alignment = min(rows_for_event, key=lambda row: row["chain_rank_by_alignment"])
            summary_rows.append(
                {
                    "event_id": exposure["event_id"],
                    "event_date": exposure["event_date"],
                    "window": window,
                    "friction_date": selected_date.isoformat(),
                    "daily_sum_rmsd": daily["sum_rmsd"],
                    "gap": daily["gap"],
                    "ranking_mode": args.ranking_mode,
                    "top_rmsd_chain": top_rmsd["chain"],
                    "top_rmsd_chain_rmsd": top_rmsd["chain_rmsd"],
                    "top_rmsd_chain_rank": top_rmsd["chain_rank_by_rmsd"],
                    "top_alignment_chain": top_alignment["chain"],
                    "top_alignment_score": top_alignment["alignment_score"],
                    "top_alignment_relevance_score": top_alignment["relevance_alignment_score"],
                    "top_alignment_impact_score": top_alignment["impact_alignment_score"],
                    "top_alignment_chain_rmsd": top_alignment["chain_rmsd"],
                    "top_alignment_chain_rmsd_rank": top_alignment["chain_rank_by_rmsd"],
                    "top_alignment_chain_alignment_rank": top_alignment["chain_rank_by_alignment"],
                    "top_alignment_chain_relevance_rank": top_alignment["chain_rank_by_relevance_alignment"],
                    "top_alignment_chain_impact_rank": top_alignment["chain_rank_by_impact_alignment"],
                    "top_alignment_currency_overlap": top_alignment["currency_overlap"],
                    "top_alignment_currency_relevance_overlap": top_alignment["currency_relevance_overlap"],
                    "top_alignment_weighted_currency_overlap": top_alignment["weighted_currency_overlap"],
                }
            )

    category_daily = _aggregate_daily_vectors(exposures, CATEGORIES, "category")
    currency_daily = _aggregate_daily_vectors(exposures, EVENT_CURRENCIES, "currency")

    _write_csv(output_dir / "event_alignment_summary.csv", summary_rows)
    _write_csv(output_dir / "event_chain_alignment.csv", chain_alignment_rows)
    _write_csv(output_dir / "waterfall_category_daily.csv", category_daily)
    _write_csv(output_dir / "waterfall_currency_daily.csv", currency_daily)

    print("ANAS x FrictionGraph alignment")
    print(f"Accepted events: {len(exposures)}")
    print(f"Event-window summaries: {len(summary_rows)}")
    print(f"Event-chain rows: {len(chain_alignment_rows)}")
    print(f"Wrote: {output_dir / 'event_alignment_summary.csv'}")
    return 0


def _load_json(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected list JSON in {source}")
    return [row for row in data if isinstance(row, dict)]


def _load_daily_rows(path: str | Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "date": _parse_date(row["date"]),
                    "sum_rmsd": _to_float(row.get("sum_rmsd")),
                    "gap": _to_float(row.get("gap")),
                    "most_positive_chain_label": row.get("most_positive_chain_label", ""),
                    "most_negative_chain_label": row.get("most_negative_chain_label", ""),
                }
            )
    return rows


def _load_chain_rows(path: str | Path) -> dict[date, list[dict[str, Any]]]:
    rows_by_date: dict[date, list[dict[str, Any]]] = defaultdict(list)
    with Path(path).open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            chain = row["chain"]
            currencies = _parse_chain_currencies(chain)
            rows_by_date[_parse_date(row["date"])].append(
                {
                    "date": _parse_date(row["date"]),
                    "chain": chain,
                    "chain_currencies": currencies,
                    "chain_rmsd": _to_float(row.get("rmsd")),
                    "mean_friction": _to_float(row.get("mean_friction")),
                    "min_friction": _to_float(row.get("min_friction")),
                    "max_friction": _to_float(row.get("max_friction")),
                    "samples_non_structural": int(float(row.get("samples_non_structural") or 0)),
                }
            )
    return rows_by_date


def _select_window_date(
    event_date: date,
    window: str,
    daily_by_date: dict[date, dict[str, Any]],
    available_dates: list[date],
) -> date | None:
    if window == "same_day":
        return event_date if event_date in daily_by_date else None
    if window == "next_day":
        for candidate in available_dates:
            if candidate > event_date:
                return candidate
        return None

    days = 3 if window == "3_day" else 7
    end_date = event_date + timedelta(days=days)
    candidates = [candidate for candidate in available_dates if event_date <= candidate <= end_date]
    if not candidates:
        return None
    return max(candidates, key=lambda candidate: daily_by_date[candidate]["sum_rmsd"])


def _score_chain(
    exposure: dict[str, Any],
    daily: dict[str, Any],
    chain_row: dict[str, Any],
    window: str,
    ranking_mode: str,
) -> dict[str, Any]:
    currency_relevance = exposure.get("currency_relevance") or exposure.get("currency_score", {})
    currency_score = exposure.get("currency_score", currency_relevance)
    currency_impact = exposure.get("currency_impact", {})
    currency_direction = exposure.get("currency_direction", {})
    chain_currencies = chain_row["chain_currencies"]

    currency_overlap = sum(_to_float(currency_score.get(ccy)) for ccy in chain_currencies)
    currency_relevance_overlap = sum(_to_float(currency_relevance.get(ccy)) for ccy in chain_currencies)
    weighted_currency_overlap = sum(
        _to_float(currency_relevance.get(ccy)) * _to_float(currency_impact.get(ccy))
        for ccy in chain_currencies
    )
    directional_currency_overlap = sum(
        abs(_to_float(currency_direction.get(ccy))) * _to_float(currency_impact.get(ccy))
        for ccy in chain_currencies
    )
    relevance_alignment_score = currency_relevance_overlap * chain_row["chain_rmsd"]
    impact_alignment_score = weighted_currency_overlap * chain_row["chain_rmsd"]
    alignment_score = relevance_alignment_score if ranking_mode == "relevance" else impact_alignment_score

    return {
        "event_id": exposure["event_id"],
        "event_date": exposure["event_date"],
        "window": window,
        "friction_date": daily["date"].isoformat(),
        "daily_sum_rmsd": daily["sum_rmsd"],
        "gap": daily["gap"],
        "chain": chain_row["chain"],
        "chain_currencies": "|".join(chain_currencies),
        "chain_rmsd": chain_row["chain_rmsd"],
        "mean_friction": chain_row["mean_friction"],
        "min_friction": chain_row["min_friction"],
        "max_friction": chain_row["max_friction"],
        "samples_non_structural": chain_row["samples_non_structural"],
        "currency_overlap": currency_overlap,
        "currency_relevance_overlap": currency_relevance_overlap,
        "weighted_currency_overlap": weighted_currency_overlap,
        "directional_currency_overlap": directional_currency_overlap,
        "relevance_alignment_score": relevance_alignment_score,
        "impact_alignment_score": impact_alignment_score,
        "alignment_score": alignment_score,
    }


def _aggregate_daily_vectors(
    exposures: list[dict[str, Any]],
    keys: list[str],
    prefix: str,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, float]] = {}
    for exposure in exposures:
        event_date = exposure["event_date"]
        scores = exposure.get(f"{prefix}_relevance") or exposure.get(f"{prefix}_score", {})
        directions = exposure.get(f"{prefix}_direction", {})
        impacts = exposure.get(f"{prefix}_impact", {})
        for key in keys:
            score = _to_float(scores.get(key))
            direction = _to_float(directions.get(key))
            impact = _to_float(impacts.get(key))
            bucket = grouped.setdefault(
                (event_date, key),
                {"score": 0.0, "max_impact": 0.0, "direction_x_impact": 0.0, "impact_sum": 0.0},
            )
            bucket["score"] = max(bucket["score"], score)
            bucket["max_impact"] = max(bucket["max_impact"], impact)
            bucket["direction_x_impact"] += direction * impact
            bucket["impact_sum"] += impact

    rows = []
    dimension = "category" if prefix == "category" else "currency"
    for (event_date, key), bucket in sorted(grouped.items()):
        impact_sum = bucket["impact_sum"]
        daily_direction = bucket["direction_x_impact"] / impact_sum if impact_sum else 0.0
        rows.append(
            {
                "date": event_date,
                dimension: key,
                "score": bucket["score"],
                "direction": daily_direction,
                "impact": bucket["max_impact"],
            }
        )
    return rows


def _assign_rank(rows: list[dict[str, Any]], value_key: str, rank_key: str) -> None:
    sorted_rows = sorted(rows, key=lambda row: row[value_key], reverse=True)
    last_value = None
    last_rank = 0
    for index, row in enumerate(sorted_rows, 1):
        value = row[value_key]
        if value != last_value:
            last_rank = index
            last_value = value
        row[rank_key] = last_rank


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _parse_chain_currencies(chain: str) -> list[str]:
    currencies = [part.strip() for part in chain.split("->")]
    if len(currencies) >= 2 and currencies[-1] == currencies[0]:
        currencies = currencies[:-1]
    return currencies


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


if __name__ == "__main__":
    raise SystemExit(main())
