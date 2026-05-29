#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import html as html_lib
from html.parser import HTMLParser
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

from anas.events.connectors import browser_headers
from anas.events.schemas import SeedEventSet
from anas.progress import ProgressBar


DEFAULT_OUTPUT = "data/seeds/general_events_2024_2025_seed_v1.json"


@dataclass(frozen=True)
class SourceSpec:
    key: str
    source: str
    source_policy_id: str
    document_type: str
    index_urls: list[str]
    allowed_hosts: tuple[str, ...]
    include_patterns: tuple[str, ...]
    exclude_patterns: tuple[str, ...]
    categories: list[str]
    country_focus: list[str]
    currency_focus: list[str]
    alignment_note: str
    max_links: int | None = None
    quiet_failures: bool = False
    exclude_title_patterns: tuple[str, ...] = ()


MONTH_NAMES = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href")
        if href:
            self._href = href
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            text = data.strip()
            if text:
                self._text_parts.append(text)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, " ".join(self._text_parts).strip()))
            self._href = None
            self._text_parts = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a broad 2024-2025 official-event seed for ANAS")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--years", default="2024,2025")
    parser.add_argument("--limit", type=int, default=None, help="Limit final seed size after sorting/deduping")
    parser.add_argument(
        "--sampling",
        choices=["chronological", "balanced"],
        default="balanced",
        help="How to choose rows when --limit is set",
    )
    parser.add_argument(
        "--per-source-limit",
        type=int,
        default=None,
        help="Limit events kept per source before the final global limit",
    )
    parser.add_argument("--source", action="append", default=None, help="Source key to include; repeatable")
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--force", action="store_true", help="Ignore checkpoint and rebuild from scratch")
    parser.add_argument(
        "--no-resolve-detail-dates",
        action="store_true",
        help="Do not fetch detail pages to recover exact publication dates",
    )
    parser.add_argument(
        "--no-materiality-filter",
        action="store_true",
        help="Keep administrative/low-signal releases instead of filtering for material policy/economic events",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output_path.with_suffix(output_path.suffix + ".checkpoint.json")

    years = [year.strip() for year in args.years.split(",") if year.strip()]
    year_set = {int(year) for year in years}
    specs = _source_specs(years)
    if args.source:
        wanted = set(args.source)
        specs = [spec for spec in specs if spec.key in wanted]

    checkpoint = {"completed_index_urls": [], "events": []}
    if checkpoint_path.exists() and not args.force:
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))

    completed = set(checkpoint.get("completed_index_urls", []))
    events_by_id = {
        event["event_id"]: event
        for event in checkpoint.get("events", [])
        if _event_year_allowed(event.get("event_date", ""), year_set)
    }

    tasks = [(spec, url) for spec in specs for url in _unique(spec.index_urls) if url not in completed]
    print("ANAS general official-event seed builder")
    print(f"Years: {', '.join(years)}")
    print(f"Sources: {', '.join(spec.key for spec in specs)}")
    print(f"Checkpoint: {checkpoint_path}")
    print(f"Pending index pages: {len(tasks)}")

    progress = ProgressBar(total=len(tasks), label="seed")
    for done, (spec, index_url) in enumerate(tasks, 1):
        progress.update(done - 1, current=spec.key, extra=index_url[:55])
        try:
            discovered = fetch_index_events(
                spec,
                index_url,
                timeout=args.timeout,
                allowed_years=year_set,
                resolve_detail_dates=not args.no_resolve_detail_dates,
                materiality_filter=not args.no_materiality_filter,
            )
        except Exception as exc:
            if not spec.quiet_failures:
                progress.newline()
                print(f"warning: failed index {spec.key} {index_url}: {exc}")
            completed.add(index_url)
            _write_checkpoint(checkpoint_path, completed, events_by_id)
            progress.update(done, current=spec.key, extra="error")
            continue

        for event in discovered:
            events_by_id[event["event_id"]] = event
        completed.add(index_url)
        _write_checkpoint(checkpoint_path, completed, events_by_id)
        progress.update(done, current=spec.key, extra=f"events={len(events_by_id)}")

    if tasks:
        progress.finish(message=f"events={len(events_by_id)}")

    events = sorted(events_by_id.values(), key=lambda row: (row["event_date"], row["event_id"]))
    if args.per_source_limit is not None:
        events = _limit_per_source(events, args.per_source_limit)
    if args.limit is not None and args.sampling == "balanced":
        events = _balanced_limit(events, args.limit)
    elif args.limit is not None:
        events = events[: args.limit]

    seed_payload = {
        "version": output_path.stem,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_document": "docs/general_event_waterfall.md",
        "frictiongraph_alignment_space": {
            "chain_currencies": ["CAD", "CHF", "EUR", "JPY", "SGD", "USD"],
            "proxy_instruments": ["CNH", "XAU"],
            "triangle_chain_count": 32,
            "reference_files": [
                "data/reference/frictiongraph_universe.json",
                "data/reference/frictiongraph_chains.json",
                "data/reference/frictiongraph_chains.csv",
            ],
        },
        "events": events,
    }
    SeedEventSet.model_validate(seed_payload)
    output_path.write_text(json.dumps(seed_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(events)} events to {output_path}")
    _print_source_counts(events)
    return 0


def fetch_index_events(
    spec: SourceSpec,
    index_url: str,
    *,
    timeout: int,
    allowed_years: set[int],
    resolve_detail_dates: bool,
    materiality_filter: bool,
) -> list[dict[str, Any]]:
    response = requests.get(index_url, headers=browser_headers(), timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    parser = LinkParser()
    parser.feed(response.text)

    discovered: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    candidates = [(response.url, _extract_title(response.text))]
    candidates.extend(parser.links)
    for href, title in candidates:
        url = urljoin(response.url, href)
        url = _strip_fragment(url)
        if url in seen_urls:
            continue
        seen_urls.add(url)
        if not _allowed_url(url, spec):
            continue

        detail_html = ""
        event_date = _extract_exact_date(url, title)
        if event_date is None and resolve_detail_dates:
            try:
                detail_response = requests.get(url, headers=browser_headers(), timeout=timeout, allow_redirects=True)
                detail_response.raise_for_status()
                detail_html = detail_response.text
                event_date = _extract_exact_date(detail_response.url, detail_html[:12000])
            except Exception:
                event_date = None
        if event_date is None or not _event_year_allowed(event_date, allowed_years):
            continue
        title = _clean_title(title) or _extract_title(detail_html) or _title_from_url(url)
        if not title or len(title) < 8:
            continue
        if _excluded_title(title, spec):
            continue
        if materiality_filter and not _is_material_event(title, spec):
            continue
        event_id = _event_id(spec.key, event_date, title, url)
        discovered.append(
            {
                "event_id": event_id,
                "event_date": event_date,
                "source_policy_id": spec.source_policy_id,
                "source": spec.source,
                "document_type": spec.document_type,
                "title": title,
                "source_url": url,
                "primary_categories": spec.categories,
                "country_focus": spec.country_focus,
                "currency_focus": spec.currency_focus,
                "alignment_note": spec.alignment_note,
            }
        )
        if spec.max_links and len(discovered) >= spec.max_links:
            break
    return discovered


def _source_specs(years: list[str]) -> list[SourceSpec]:
    return [
        SourceSpec(
            key="fed",
            source="Federal Reserve Board",
            source_policy_id="fed_board_public_domain",
            document_type="fed_press_release",
            index_urls=[f"https://www.federalreserve.gov/newsevents/pressreleases/{year}-press.htm" for year in years],
            allowed_hosts=("www.federalreserve.gov", "federalreserve.gov"),
            include_patterns=(r"/newsevents/pressreleases/",),
            exclude_patterns=(r"/files/", r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(
                r"\bdesignation of the chairs\b",
                r"\bannounces .* members of its .* council\b",
                r"\bapproval of proposal\b",
                r"\btermination of enforcement action\b",
                r"\benforcement action with\b",
                r"\benforcement actions with former employee\b",
            ),
            categories=["monetary_policy", "inflation", "macro_growth", "equities_risk"],
            country_focus=["US"],
            currency_focus=["USD", "JPY", "EUR", "CHF", "CAD", "SGD"],
            alignment_note="Federal Reserve official communication maps to USD policy, global rates, and risk channels.",
        ),
        SourceSpec(
            key="treasury",
            source="U.S. Treasury / OFAC",
            source_policy_id="treasury_ofac_official",
            document_type="treasury_press_release",
            index_urls=[
                f"https://home.treasury.gov/news/press-releases?field_press_release_date_value%5Bvalue%5D%5Byear%5D={year}"
                for year in years
            ]
            + [f"https://home.treasury.gov/news/press-releases?page={page}" for page in range(0, 16)],
            allowed_hosts=("home.treasury.gov",),
            include_patterns=(r"/news/press-releases/",),
            exclude_patterns=(r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(
                r"\bremarks by\b",
                r"\breadout\b",
                r"\bjoint statement on the eu-u\.s\. joint financial regulatory forum\b",
            ),
            categories=["sanctions", "geopolitics", "fiscal_policy", "macro_growth"],
            country_focus=["US"],
            currency_focus=["USD", "CHF", "JPY", "EUR", "XAU"],
            alignment_note="Treasury/OFAC official releases map to sanctions, fiscal policy, geopolitics, USD funding, and safe-haven channels.",
        ),
        SourceSpec(
            key="bea",
            source="Bureau of Economic Analysis",
            source_policy_id="bea_public_domain",
            document_type="bea_news_release",
            index_urls=[f"https://www.bea.gov/news/{year}" for year in years],
            allowed_hosts=("www.bea.gov", "bea.gov"),
            include_patterns=(r"/news/\d{4}/",),
            exclude_patterns=(r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(r"\bschedule\b", r"\btechnical note\b"),
            categories=["macro_growth", "inflation", "equities_risk"],
            country_focus=["US"],
            currency_focus=["USD", "CAD", "EUR", "JPY", "CHF"],
            alignment_note="BEA macro releases map to U.S. growth, inflation, income, trade, and USD macro channels.",
        ),
        SourceSpec(
            key="eia",
            source="U.S. Energy Information Administration",
            source_policy_id="eia_public_domain",
            document_type="eia_press_release",
            index_urls=[f"https://www.eia.gov/pressroom/releases/press{number}.php" for number in range(545, 581)]
            + ["https://www.eia.gov/pressroom/releases.php"],
            allowed_hosts=("www.eia.gov", "eia.gov"),
            include_patterns=(r"/pressroom/releases/press\d+\.php$",),
            exclude_patterns=(r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(r"\bindependent statistics and analysis\b",),
            categories=["energy_oil_gas", "inflation", "macro_growth", "commodities_metals"],
            country_focus=["US"],
            currency_focus=["USD", "CAD", "JPY", "CHF"],
            alignment_note="EIA official releases map to energy, oil/gas, inflation, CAD energy sensitivity, and safe-haven channels.",
            quiet_failures=True,
        ),
        SourceSpec(
            key="whitehouse",
            source="White House",
            source_policy_id="white_house_official",
            document_type="white_house_release",
            index_urls=[
                "https://www.whitehouse.gov/briefings-statements/",
                *[f"https://www.whitehouse.gov/briefings-statements/page/{page}/" for page in range(2, 26)],
                "https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/",
                *[
                    f"https://bidenwhitehouse.archives.gov/briefing-room/statements-releases/page/{page}/"
                    for page in range(2, 26)
                ],
            ],
            allowed_hosts=("www.whitehouse.gov", "bidenwhitehouse.archives.gov"),
            include_patterns=(r"/briefing-room/", r"/briefings-statements/"),
            exclude_patterns=(r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(
                r"\bnominations? and withdrawals?\b",
                r"\bpresident .* announces nominees\b",
                r"\bbill signed\b",
                r"\bstatement .* on the passing of\b",
                r"\bstatement .* on .* birthday\b",
                r"\bmeeting with families\b",
            ),
            categories=["geopolitics", "trade_policy", "fiscal_policy", "macro_growth", "defense_security"],
            country_focus=["US"],
            currency_focus=["USD", "EUR", "JPY", "CHF", "CAD", "SGD", "CNH"],
            alignment_note="White House official releases map to broad U.S. policy, geopolitics, trade, fiscal, and risk channels.",
        ),
        SourceSpec(
            key="ustr",
            source="Office of the U.S. Trade Representative",
            source_policy_id="ustr_official_releases",
            document_type="ustr_press_release",
            index_urls=[
                f"https://ustr.gov/about-us/policy-offices/press-office/press-releases/{year}"
                for year in years
            ],
            allowed_hosts=("ustr.gov", "www.ustr.gov"),
            include_patterns=(r"/press-releases/\d{4}/",),
            exclude_patterns=(r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(
                r"\bto travel to\b",
                r"\bweek ahead guidance\b",
                r"\bsummary of u\.s\. mission\b",
                r"\bicymi\b",
                r"\bcelebrating .* month\b",
                r"\bdeparture of\b",
            ),
            categories=["trade_policy", "geopolitics", "supply_chain", "semiconductors", "commodities_metals"],
            country_focus=["US"],
            currency_focus=["USD", "CNH", "SGD", "JPY", "CHF", "EUR", "CAD"],
            alignment_note="USTR official releases map to trade policy, tariff, supply-chain, China proxy, and Asia trade channels.",
        ),
        SourceSpec(
            key="commerce_bis",
            source="U.S. Department of Commerce / BIS",
            source_policy_id="commerce_bis_official",
            document_type="commerce_bis_release",
            index_urls=[
                "https://www.bis.gov/press-release",
                "https://www.bis.gov/newsroom",
            ],
            allowed_hosts=("www.bis.gov", "bis.gov"),
            include_patterns=(r"/press-release/", r"/newsroom/"),
            exclude_patterns=(r"\.pdf$", r"\.zip$"),
            exclude_title_patterns=(r"\badvisory committee\b",),
            categories=["semiconductors", "artificial_intelligence", "trade_policy", "geopolitics", "defense_security"],
            country_focus=["US", "CN"],
            currency_focus=["USD", "CNH", "SGD", "JPY", "CHF"],
            alignment_note="Commerce/BIS official releases map to export controls, semiconductors, AI compute, defense, and China proxy channels.",
        ),
    ]


def _allowed_url(url: str, spec: SourceSpec) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path
    if host not in spec.allowed_hosts:
        return False
    if any(re.search(pattern, url, re.IGNORECASE) for pattern in spec.exclude_patterns):
        return False
    return any(re.search(pattern, url, re.IGNORECASE) for pattern in spec.include_patterns)


def _excluded_title(title: str, spec: SourceSpec) -> bool:
    return any(re.search(pattern, title, re.IGNORECASE) for pattern in spec.exclude_title_patterns)


def _is_material_event(title: str, spec: SourceSpec) -> bool:
    title_l = title.lower()
    source_rules = {
        "fed": (
            "fomc",
            "federal open market committee",
            "monetary",
            "discount rate",
            "interest rate",
            "bank term funding",
            "stress test",
            "hypothetical scenarios",
            "financial stability",
            "capital",
            "liquidity",
            "risk management",
            "community reinvestment",
        ),
        "treasury": (
            "sanction",
            "ofac",
            "iran",
            "russia",
            "houthi",
            "cartel",
            "maduro",
            "venezuela",
            "terror",
            "illicit finance",
            "fincen",
            "financial stability",
            "fsoc",
            "treasury international capital",
            "tax",
            "oil",
            "cybersecurity",
        ),
        "bea": (
            "gross domestic product",
            "gdp",
            "personal income",
            "personal consumption",
            "international trade",
            "current account",
            "inflation",
            "prices",
            "corporate profits",
        ),
        "eia": (
            "oil",
            "gasoline",
            "natural gas",
            "electricity",
            "energy",
            "crude",
            "petroleum",
            "coal",
            "steo",
            "short-term energy outlook",
        ),
        "whitehouse": (
            "sanction",
            "tariff",
            "chips",
            "semiconductor",
            "supply chain",
            "inflation",
            "economic",
            "g20",
            "g7",
            "china",
            "japan",
            "korea",
            "russia",
            "ukraine",
            "iran",
            "energy",
            "infrastructure",
            "climate",
            "financial",
            "trade",
        ),
        "ustr": (
            "tariff",
            "section 301",
            "usmca",
            "trade",
            "wto",
            "china",
            "taiwan",
            "supply chain",
            "critical minerals",
            "labor mechanism",
            "market access",
            "autos",
            "agreement",
            "dispute",
        ),
        "commerce_bis": (
            "export control",
            "semiconductor",
            "advanced computing",
            "artificial intelligence",
            "ai",
            "china",
            "entity list",
            "military",
            "national security",
            "supply chain",
        ),
    }
    keywords = source_rules.get(spec.key, ())
    return any(keyword in title_l for keyword in keywords)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _extract_exact_date(url: str, title_or_html: str) -> str | None:
    haystack = f"{url} {title_or_html}"
    for pattern in [
        r"(20\d{2})[-_/](\d{1,2})[-_/](\d{1,2})",
        r"(20\d{2})(\d{2})(\d{2})",
    ]:
        match = re.search(pattern, haystack, re.IGNORECASE)
        if match:
            year, month, day = (int(part) for part in match.groups())
            return _format_valid_date(year, month, day)

    month_pattern = "|".join(sorted(MONTH_NAMES, key=len, reverse=True))
    match = re.search(
        rf"\b({month_pattern})\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(20\d{{2}})\b",
        haystack,
        re.IGNORECASE,
    )
    if match:
        month = MONTH_NAMES[match.group(1).lower().rstrip(".")]
        day = int(match.group(2))
        year = int(match.group(3))
        return _format_valid_date(year, month, day)

    match = re.search(
        rf"\b(\d{{1,2}})\s+({month_pattern})\.?\s+(20\d{{2}})\b",
        haystack,
        re.IGNORECASE,
    )
    if match:
        day = int(match.group(1))
        month = MONTH_NAMES[match.group(2).lower().rstrip(".")]
        year = int(match.group(3))
        return _format_valid_date(year, month, day)
    return None


def _format_valid_date(year: int, month: int, day: int) -> str | None:
    try:
        return datetime(year, month, day).date().isoformat()
    except ValueError:
        return None


def _event_year_allowed(event_date: str, allowed_years: set[int]) -> bool:
    try:
        return int(event_date[:4]) in allowed_years
    except (TypeError, ValueError):
        return False


def _extract_title(html: str) -> str:
    if not html:
        return ""
    for pattern in [
        r"<h1[^>]*>(.*?)</h1>",
        r"<title[^>]*>(.*?)</title>",
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
    ]:
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if match:
            title = html_lib.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))
            return _clean_title(title)
    return ""


def _limit_per_source(events: list[dict[str, Any]], per_source_limit: int) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    kept: list[dict[str, Any]] = []
    for event in events:
        key = event["source_policy_id"]
        counts[key] = counts.get(key, 0)
        if counts[key] >= per_source_limit:
            continue
        kept.append(event)
        counts[key] += 1
    return kept


def _balanced_limit(events: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    by_source: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        by_source.setdefault(event["source_policy_id"], []).append(event)

    selected: list[dict[str, Any]] = []
    source_ids = sorted(by_source)
    while len(selected) < limit and source_ids:
        next_source_ids: list[str] = []
        for source_id in source_ids:
            bucket = by_source[source_id]
            if bucket and len(selected) < limit:
                selected.append(bucket.pop(0))
            if bucket:
                next_source_ids.append(source_id)
        source_ids = next_source_ids
    return sorted(selected, key=lambda row: (row["event_date"], row["event_id"]))


def _print_source_counts(events: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for event in events:
        counts[event["source"]] = counts.get(event["source"], 0) + 1
    if not counts:
        return
    print("Source counts:")
    for source, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"- {source}: {count}")


def _event_id(source_key: str, event_date: str, title: str, url: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")
    slug = "_".join(slug.split("_")[:10]) or re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[-40:]
    return f"{source_key}_{event_date.replace('-', '_')}_{slug}"[:140]


def _title_from_url(url: str) -> str:
    stem = Path(urlparse(url).path).stem
    return re.sub(r"[-_]+", " ", stem).strip().title()


def _clean_title(title: str) -> str:
    title = re.sub(r"\s+", " ", title).strip()
    title = re.sub(r"^(Press Release|Statement|Fact Sheet):\s*", "", title, flags=re.IGNORECASE)
    return title


def _strip_fragment(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(fragment="").geturl()


def _write_checkpoint(path: Path, completed: set[str], events_by_id: dict[str, dict[str, Any]]) -> None:
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "completed_index_urls": sorted(completed),
        "events": sorted(events_by_id.values(), key=lambda row: (row["event_date"], row["event_id"])),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
