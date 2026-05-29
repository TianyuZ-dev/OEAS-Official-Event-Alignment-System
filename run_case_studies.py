#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_THEME_CATEGORIES = {
    "geopolitics",
    "trade_policy",
    "sanctions",
    "energy_oil_gas",
    "semiconductors",
    "artificial_intelligence",
    "supply_chain",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build readable ANAS x FrictionGraph case studies")
    parser.add_argument("--seed", default="data/seeds/official_events_seed_v1.json")
    parser.add_argument("--exposures", default="output/events/accepted_exposures_latest.json")
    parser.add_argument("--summary", default="output/alignment/event_alignment_summary.csv")
    parser.add_argument("--chains", default="output/alignment/event_chain_alignment.csv")
    parser.add_argument("--output-dir", default="output/cases")
    parser.add_argument("--basename", default="case_studies_v1")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--event-id", action="append", default=None, help="Specific event_id to include; repeatable")
    parser.add_argument(
        "--theme",
        choices=["geopolitical_trade", "all"],
        default="geopolitical_trade",
        help="Default filters toward ANAS v1's geopolitical/trade demo narrative",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    seeds = _seed_by_id(args.seed)
    exposures = _records_by_id(_load_json(args.exposures))
    summaries = _load_csv(args.summary)
    chain_rows = _load_csv(args.chains)
    if not exposures or not summaries:
        print("Missing case inputs. Run `python3 run_event_latest.py` and `python3 run_alignment.py` first.")
        return 2

    selected_summaries = _select_case_summaries(
        summaries=summaries,
        seeds=seeds,
        limit=args.limit,
        event_ids=args.event_id,
        theme=args.theme,
    )
    if not selected_summaries:
        print("No case candidates matched the requested filters.")
        return 2

    cases = []
    for summary in selected_summaries:
        event_id = summary["event_id"]
        exposure = exposures.get(event_id)
        seed = seeds.get(event_id, {})
        if exposure is None:
            continue
        case_chain_rows = [
            row
            for row in chain_rows
            if row["event_id"] == event_id
            and row["window"] == summary["window"]
            and row["friction_date"] == summary["friction_date"]
        ]
        cases.append(
            _build_case(
                seed,
                exposure,
                summary,
                case_chain_rows,
                tableau_files=[
                    args.summary,
                    args.chains,
                    str(Path(args.summary).with_name("waterfall_category_daily.csv")),
                    str(Path(args.summary).with_name("waterfall_currency_daily.csv")),
                ],
            )
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{args.basename}.json"
    md_path = output_dir / f"{args.basename}.md"
    csv_path = output_dir / f"{args.basename}.csv"
    json_path.write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(cases, title=_title_from_basename(args.basename)), encoding="utf-8")
    _write_case_csv(csv_path, cases)

    print("ANAS case studies")
    print(f"Cases: {len(cases)}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Wrote: {csv_path}")
    return 0


def _select_case_summaries(
    summaries: list[dict[str, str]],
    seeds: dict[str, dict[str, Any]],
    limit: int,
    event_ids: list[str] | None,
    theme: str,
) -> list[dict[str, str]]:
    if event_ids:
        wanted = set(event_ids)
        candidates = [row for row in summaries if row["event_id"] in wanted]
    else:
        candidates = summaries
        if theme == "geopolitical_trade":
            candidates = [
                row
                for row in candidates
                if DEFAULT_THEME_CATEGORIES.intersection(set(seeds.get(row["event_id"], {}).get("primary_categories", [])))
            ]

    best_by_event: dict[str, dict[str, str]] = {}
    for row in candidates:
        event_id = row["event_id"]
        current = best_by_event.get(event_id)
        if current is None or _case_sort_key(row) > _case_sort_key(current):
            best_by_event[event_id] = row

    return sorted(best_by_event.values(), key=_case_sort_key, reverse=True)[:limit]


def _case_sort_key(row: dict[str, str]) -> tuple[float, float, float]:
    return (
        _to_float(row.get("top_alignment_score")),
        _to_float(row.get("daily_sum_rmsd")),
        -_to_float(row.get("top_alignment_chain_rmsd_rank")),
    )


def _build_case(
    seed: dict[str, Any],
    exposure: dict[str, Any],
    summary: dict[str, str],
    chain_rows: list[dict[str, str]],
    tableau_files: list[str],
) -> dict[str, Any]:
    top_categories = _top_dimensions(
        exposure.get("category_score", {}),
        exposure.get("category_direction", {}),
        exposure.get("category_impact", {}),
        limit=5,
    )
    top_currencies = _top_dimensions(
        exposure.get("currency_score", {}),
        exposure.get("currency_direction", {}),
        exposure.get("currency_impact", {}),
        limit=5,
    )
    top_alignment_rows = sorted(chain_rows, key=lambda row: _to_float(row.get("alignment_score")), reverse=True)[:5]
    top_rmsd_rows = sorted(chain_rows, key=lambda row: _to_float(row.get("chain_rmsd")), reverse=True)[:5]

    return {
        "case_id": f"{summary['event_id']}__{summary['window']}",
        "event_id": summary["event_id"],
        "event_date": summary["event_date"],
        "title": seed.get("title", summary["event_id"]),
        "source": seed.get("source", exposure.get("source", "")),
        "official_url": seed.get("source_url", ""),
        "window": summary["window"],
        "friction_date": summary["friction_date"],
        "dominant_categories": top_categories,
        "dominant_currencies": top_currencies,
        "alignment": {
            "daily_sum_rmsd": _to_float(summary.get("daily_sum_rmsd")),
            "gap": _to_float(summary.get("gap")),
            "ranking_mode": summary.get("ranking_mode", "impact"),
            "top_rmsd_chain": summary.get("top_rmsd_chain"),
            "top_rmsd_chain_rmsd": _to_float(summary.get("top_rmsd_chain_rmsd")),
            "top_alignment_chain": summary.get("top_alignment_chain"),
            "top_alignment_score": _to_float(summary.get("top_alignment_score")),
            "top_alignment_relevance_score": _to_float(summary.get("top_alignment_relevance_score")),
            "top_alignment_impact_score": _to_float(summary.get("top_alignment_impact_score")),
            "top_alignment_chain_rmsd": _to_float(summary.get("top_alignment_chain_rmsd")),
            "top_alignment_chain_rmsd_rank": int(_to_float(summary.get("top_alignment_chain_rmsd_rank"))),
            "top_alignment_chain_relevance_rank": int(_to_float(summary.get("top_alignment_chain_relevance_rank"))),
            "top_alignment_chain_impact_rank": int(_to_float(summary.get("top_alignment_chain_impact_rank"))),
            "top_alignment_currency_overlap": _to_float(summary.get("top_alignment_currency_overlap")),
            "top_alignment_currency_relevance_overlap": _to_float(
                summary.get("top_alignment_currency_relevance_overlap")
            ),
            "top_alignment_weighted_currency_overlap": _to_float(
                summary.get("top_alignment_weighted_currency_overlap")
            ),
        },
        "top_alignment_chains": [_chain_excerpt(row) for row in top_alignment_rows],
        "top_rmsd_chains": [_chain_excerpt(row) for row in top_rmsd_rows],
        "interpretation": _interpret_case(seed, exposure, summary),
        "caution": (
            "This case links official-event exposure to nearby FrictionGraph chain behavior. "
            "It is an explanatory alignment record, not a causal claim or trading signal."
        ),
        "tableau_ready_files": tableau_files,
    }


def _interpret_case(seed: dict[str, Any], exposure: dict[str, Any], summary: dict[str, str]) -> str:
    categories = ", ".join(_dimension_names(exposure.get("category_score", {}), limit=4))
    currencies = ", ".join(_dimension_names(exposure.get("currency_score", {}), limit=4))
    top_rmsd = summary.get("top_rmsd_chain", "")
    top_alignment = summary.get("top_alignment_chain", "")
    relation = "same chain" if top_rmsd == top_alignment else "different chains"
    return (
        f"The official event is represented by ANAS as a {categories} exposure with currency pressure around "
        f"{currencies}. In the {summary['window']} window, FrictionGraph's largest standalone RMSD chain is "
        f"{top_rmsd}, while the strongest event-overlap chain is {top_alignment}. These are {relation}, which helps "
        "separate broad market stress from event-specific currency-chain alignment."
    )


def _top_dimensions(
    scores: dict[str, Any],
    directions: dict[str, Any],
    impacts: dict[str, Any],
    limit: int,
) -> list[dict[str, Any]]:
    rows = []
    for name, score in scores.items():
        score_value = _to_float(score)
        impact_value = _to_float(impacts.get(name))
        if score_value <= 0 and impact_value <= 0:
            continue
        rows.append(
            {
                "name": name,
                "score": score_value,
                "direction": _to_float(directions.get(name)),
                "impact": impact_value,
            }
        )
    return sorted(rows, key=lambda row: (row["score"], row["impact"]), reverse=True)[:limit]


def _dimension_names(scores: dict[str, Any], limit: int) -> list[str]:
    rows = [(name, _to_float(score)) for name, score in scores.items() if _to_float(score) > 0]
    return [name for name, _ in sorted(rows, key=lambda item: item[1], reverse=True)[:limit]]


def _chain_excerpt(row: dict[str, str]) -> dict[str, Any]:
    return {
        "chain": row.get("chain", ""),
        "chain_currencies": row.get("chain_currencies", ""),
        "chain_rmsd": _to_float(row.get("chain_rmsd")),
        "chain_rank_by_rmsd": int(_to_float(row.get("chain_rank_by_rmsd"))),
        "alignment_score": _to_float(row.get("alignment_score")),
        "relevance_alignment_score": _to_float(row.get("relevance_alignment_score")),
        "impact_alignment_score": _to_float(row.get("impact_alignment_score")),
        "chain_rank_by_alignment": int(_to_float(row.get("chain_rank_by_alignment"))),
        "chain_rank_by_relevance_alignment": int(_to_float(row.get("chain_rank_by_relevance_alignment"))),
        "chain_rank_by_impact_alignment": int(_to_float(row.get("chain_rank_by_impact_alignment"))),
        "currency_overlap": _to_float(row.get("currency_overlap")),
        "currency_relevance_overlap": _to_float(row.get("currency_relevance_overlap")),
        "weighted_currency_overlap": _to_float(row.get("weighted_currency_overlap")),
    }


def _render_markdown(cases: list[dict[str, Any]], *, title: str = "ANAS Case Studies v1") -> str:
    lines = [
        f"# {title}",
        "",
        "These cases connect license-safe official event records to FrictionGraph's processed FX chain outputs.",
        "They are designed for explanation, Tableau annotation, and portfolio review, not prediction claims.",
        "",
    ]
    for index, case in enumerate(cases, 1):
        alignment = case["alignment"]
        lines.extend(
            [
                f"## {index}. {case['title']}",
                "",
                f"- Event ID: `{case['event_id']}`",
                f"- Event date: `{case['event_date']}`",
                f"- Source: {case['source']}",
                f"- Official URL: {case['official_url']}",
                f"- Selected window: `{case['window']}` ending on `{case['friction_date']}`",
                f"- Daily sum RMSD: `{alignment['daily_sum_rmsd']:.12f}`",
                f"- Ranking mode: `{alignment['ranking_mode']}`",
                f"- Top RMSD chain: `{alignment['top_rmsd_chain']}`",
                f"- Top event-alignment chain: `{alignment['top_alignment_chain']}`",
                f"- Top alignment chain RMSD rank: `{alignment['top_alignment_chain_rmsd_rank']}`",
                f"- Alignment score: `{alignment['top_alignment_score']:.12f}`",
                f"- Relevance alignment score: `{alignment['top_alignment_relevance_score']:.12f}`",
                f"- Impact alignment score: `{alignment['top_alignment_impact_score']:.12f}`",
                "",
                "### Dominant Categories",
                "",
            ]
        )
        lines.extend(_dimension_markdown(case["dominant_categories"]))
        lines.extend(["", "### Dominant Currencies", ""])
        lines.extend(_dimension_markdown(case["dominant_currencies"]))
        lines.extend(
            [
                "",
                "### Interpretation",
                "",
                case["interpretation"],
                "",
                "Caution: " + case["caution"],
                "",
                "### Tableau Inputs",
                "",
            ]
        )
        lines.extend(f"- `{path}`" for path in case["tableau_ready_files"])
        lines.append("")
    return "\n".join(lines)


def _write_case_csv(path: Path, cases: list[dict[str, Any]]) -> None:
    fieldnames = [
        "case_id",
        "event_id",
        "event_date",
        "title",
        "source",
        "official_url",
        "window",
        "friction_date",
        "daily_sum_rmsd",
        "gap",
        "top_rmsd_chain",
        "top_rmsd_chain_rmsd",
        "top_alignment_chain",
        "top_alignment_score",
        "top_alignment_relevance_score",
        "top_alignment_impact_score",
        "top_alignment_chain_rmsd",
        "top_alignment_chain_rmsd_rank",
        "top_alignment_chain_relevance_rank",
        "top_alignment_chain_impact_rank",
        "top_alignment_currency_overlap",
        "top_alignment_currency_relevance_overlap",
        "top_alignment_weighted_currency_overlap",
        "dominant_categories",
        "dominant_currencies",
        "interpretation",
        "caution",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            alignment = case["alignment"]
            writer.writerow(
                {
                    "case_id": case["case_id"],
                    "event_id": case["event_id"],
                    "event_date": case["event_date"],
                    "title": case["title"],
                    "source": case["source"],
                    "official_url": case["official_url"],
                    "window": case["window"],
                    "friction_date": case["friction_date"],
                    "daily_sum_rmsd": alignment["daily_sum_rmsd"],
                    "gap": alignment["gap"],
                    "top_rmsd_chain": alignment["top_rmsd_chain"],
                    "top_rmsd_chain_rmsd": alignment["top_rmsd_chain_rmsd"],
                    "top_alignment_chain": alignment["top_alignment_chain"],
                    "top_alignment_score": alignment["top_alignment_score"],
                    "top_alignment_relevance_score": alignment["top_alignment_relevance_score"],
                    "top_alignment_impact_score": alignment["top_alignment_impact_score"],
                    "top_alignment_chain_rmsd": alignment["top_alignment_chain_rmsd"],
                    "top_alignment_chain_rmsd_rank": alignment["top_alignment_chain_rmsd_rank"],
                    "top_alignment_chain_relevance_rank": alignment["top_alignment_chain_relevance_rank"],
                    "top_alignment_chain_impact_rank": alignment["top_alignment_chain_impact_rank"],
                    "top_alignment_currency_overlap": alignment["top_alignment_currency_overlap"],
                    "top_alignment_currency_relevance_overlap": alignment[
                        "top_alignment_currency_relevance_overlap"
                    ],
                    "top_alignment_weighted_currency_overlap": alignment[
                        "top_alignment_weighted_currency_overlap"
                    ],
                    "dominant_categories": _join_dimension_names(case["dominant_categories"]),
                    "dominant_currencies": _join_dimension_names(case["dominant_currencies"]),
                    "interpretation": case["interpretation"],
                    "caution": case["caution"],
                }
            )


def _join_dimension_names(rows: list[dict[str, Any]]) -> str:
    return "; ".join(row["name"] for row in rows)


def _title_from_basename(basename: str) -> str:
    acronyms = {"jpy": "JPY", "fx": "FX", "usd": "USD", "v1": "v1"}
    words = []
    for part in basename.replace("-", "_").split("_"):
        words.append(acronyms.get(part.lower(), part.capitalize()))
    return " ".join(words)


def _dimension_markdown(rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return ["- None"]
    return [
        f"- `{row['name']}` score={row['score']:.0f}, impact={row['impact']:.0f}, direction={row['direction']:.0f}"
        for row in rows
    ]


def _seed_by_id(path: str | Path) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {event["event_id"]: event for event in data.get("events", [])}


def _records_by_id(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {record["event_id"]: record for record in records if "event_id" in record}


def _load_json(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.exists():
        return []
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected list JSON in {source}")
    return [row for row in data if isinstance(row, dict)]


def _load_csv(path: str | Path) -> list[dict[str, str]]:
    source = Path(path)
    if not source.exists():
        return []
    with source.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _to_float(value: Any) -> float:
    if value in (None, ""):
        return 0.0
    return float(value)


if __name__ == "__main__":
    raise SystemExit(main())
