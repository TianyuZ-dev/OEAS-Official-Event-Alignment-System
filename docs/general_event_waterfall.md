# General Event Waterfall Design

This document defines the broad ANAS waterfall layer.

The purpose is different from the JPY stress case study:

- the JPY case proves that ANAS can align official-event exposure with a
  specific FrictionGraph market-structure stress window
- the general waterfall proves that ANAS can ingest a broad official-event
  stream and turn it into a stable, Tableau-ready event intelligence surface

## Core Principle

Official events are naturally sparse.

ANAS should not pretend that every day has every kind of event. Blank cells in
the raw event waterfall are not missing data. They mean:

```text
No selected official event was observed for that category on that day.
```

This matters because the project is meant to be auditable. A sparse raw event
layer is more honest than a fully filled chart that creates false continuity.

## Three Tableau Layers

### 1. Raw Event Waterfall

Purpose:

```text
Show where official-event pressure actually occurred.
```

Shape:

```text
x-axis: date
y-axis: ANAS category
color: direction
intensity: impact or relevance
tooltip: event title, source, official URL, event_id
```

Expected behavior:

- many blank days
- event clusters around policy releases, sanctions, tariff announcements,
  central-bank communication, inflation releases, energy reports, and official
  geopolitical actions
- no interpolation

Tableau input:

```text
output/waterfall_general/raw_event_category_daily.csv
```

Recommended fields:

```text
date
category
event_count
max_relevance
max_impact
weighted_direction
source_count
top_event_id
top_event_title
top_source
top_official_url
```

### 2. Decayed Daily State Waterfall

Purpose:

```text
Show how official-event pressure persists after event dates.
```

This is a derived layer, not raw observed events.

Example decay:

```text
same day: 1.00
day + 1: 0.70
day + 3: 0.40
day + 7: 0.15
day + 14: 0.00
```

Formula:

```text
daily_state[date, category] =
  sum(event_relevance * event_impact * decay(days_since_event))
```

This layer can fill more of the daily grid while staying honest because the
signal is explicitly labeled as derived.

Tableau input:

```text
output/waterfall_general/decayed_category_daily.csv
```

Recommended fields:

```text
date
category
decayed_relevance
decayed_impact
decayed_direction
active_event_count
top_contributing_event_id
top_contributing_event_title
```

### 3. Event Marker / Annotation Table

Purpose:

```text
Let Tableau tooltips explain the visible cells.
```

Tableau input:

```text
output/waterfall_general/event_annotations.csv
```

Recommended fields:

```text
event_id
event_date
source
title
official_url
primary_categories
top_currencies
relevance_summary
impact_summary
rationale
content_sha256
text_sha256
```

## Category Dimension

Use the current 16-category taxonomy:

```text
macro_growth
monetary_policy
inflation
fiscal_policy
geopolitics
trade_policy
sanctions
energy_oil_gas
commodities_metals
semiconductors
artificial_intelligence
supply_chain
defense_security
elections_policy
equities_risk
crypto_digital_assets
```

The broad waterfall should start with category rows. Currency and source rows
can be added as secondary sheets.

## Source Scope

For the broad U.S. official-event layer, start with license-safe official
sources:

```text
Federal Reserve
U.S. Treasury / OFAC
USTR
Commerce / BIS
BLS
BEA
EIA
White House
Federal Register
SEC EDGAR metadata or selected filing metadata only
```

Avoid copyrighted news full text. News links can be used later as references,
but the first portfolio version should rely on official source documents.

## First Data Scale

The first useful general waterfall should target:

```text
date range: 2024-01-01 through 2025-12-31
events: 300 to 1000 official documents
categories: 16
granularity: daily
```

This produces a grid of:

```text
731 days * 16 categories = 11,696 date-category cells
```

The raw event layer will be sparse. That is expected.

The decayed daily state layer can be much denser, but it must be labeled as
derived.

## Storage Estimate

The current ANAS sample gives a practical local baseline.

Observed local outputs:

```text
output/events:
  10 documents
  total folder size: about 1.8 MB
  raw_documents.jsonl: about 1.47 MB
  read_documents_latest.json: about 167 KB

output/events_jpy_stress:
  9 valid documents
  total folder size: about 1.0 MB
  raw_documents.jsonl: about 694 KB
  read_documents_latest.json: about 117 KB
```

Observed document text size:

```text
official_events sample:
  avg cleaned text: about 15.5k chars/document
  avg words: about 2.2k words/document

JPY stress sample:
  avg cleaned text: about 11.9k chars/document
  avg words: about 1.8k words/document
```

Practical planning assumptions:

```text
cleaned text + metadata: 15 KB to 40 KB per document
raw HTML/text JSONL: 80 KB to 200 KB per document
LLM exposure + judgment: 5 KB to 15 KB per document
alignment / waterfall derived CSV: small, usually under 100 MB for v1
```

Estimated local storage for 2024-2025:

| event count | light HTML/text only | mixed official docs | conservative local budget |
| ---: | ---: | ---: | ---: |
| 300 | 30-80 MB | 100-300 MB | 0.5 GB |
| 1,000 | 100-300 MB | 300 MB-1.5 GB | 2 GB |
| 5,000 | 500 MB-1.5 GB | 2-8 GB | 10 GB |

If ANAS stores original PDF/XLSX binaries, budget more:

```text
small PDFs / XLSX: 100 KB to 1 MB each
large official reports: 2 MB to 20 MB each
```

For a 2024-2025 portfolio-scale run, a safe local estimate is:

```text
300-1000 events with raw text + selected original files:
  about 0.5 GB to 2 GB
```

If every linked attachment is archived aggressively:

```text
1000 events:
  about 2 GB to 10 GB
```

This is manageable locally. AWS S3 becomes useful when:

- the corpus grows beyond several thousand events
- original PDFs/XLSX are preserved as binary objects
- multiple runs need versioned storage
- the project needs portfolio evidence of cloud data engineering

## Storage Policy Recommendation

For v1, use a three-tier storage policy:

### Tier 1: Always Keep

```text
event metadata
official URL
final URL
content_sha256
text_sha256
cleaned text
exposure struct
judgment
alignment outputs
Tableau CSVs
```

### Tier 2: Keep For Important Events

```text
original PDF/XLSX binary
raw HTML response
HTML/PDF extraction diagnostics
case-study snapshots
```

### Tier 3: Store In S3 Later

```text
large binary archives
full run snapshots
versioned training datasets
model fine-tuning corpora
```

This keeps the local project lightweight while preserving a clean path to AWS.

## Why Sparse Is Good

The waterfall should make a clear distinction:

```text
raw official events are sparse
derived daily pressure can be continuous
market-side FrictionGraph data is daily
```

That gives the final demo a strong structure:

```text
Layer 1: broad official-event waterfall
Layer 2: decayed daily event-pressure state
Layer 3: specific FrictionGraph alignment case studies
Layer 4: training-ready structured data for future small models
```

This tells a complete portfolio story:

```text
source policy
official document ingestion
LLM struct extraction
Tableau visualization
market alignment
future model training
```

## Next Engineering Steps

1. Build `run_waterfall_general.py`.
2. Add a source-specific event indexer for each official source.
3. Produce `raw_event_category_daily.csv`.
4. Produce `decayed_category_daily.csv`.
5. Produce `event_annotations.csv`.
6. Create a Tableau manifest that explains joins and recommended sheets.

The first implementation can use the existing 10-event and JPY seed outputs to
validate the waterfall format before scaling to hundreds of events.
