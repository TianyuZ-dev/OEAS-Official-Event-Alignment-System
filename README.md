# ANAS - Autonomous News Analysis System

ANAS is a license-safe official-event intelligence pipeline for market-structure research.

It ingests official public documents, converts them into structured category/currency exposure vectors with LLM agents, validates the output with schema guardrails and a judge agent, and aligns accepted exposures with FrictionGraph FX-chain stress outputs.

This repository is a portfolio-ready public version. It contains code, schemas, documentation, seed metadata, and small derived Tableau exports. It intentionally excludes private API keys, raw fetched documents, and large local market-data files.

## Project Idea

FrictionGraph measures when FX market structure becomes internally inconsistent through triangular currency-chain friction.

ANAS adds the event-intelligence layer:

```text
official event document
  -> cleaned text + content hash
  -> LLM exposure struct
  -> judge / schema validation
  -> category and currency waterfalls
  -> FrictionGraph chain alignment
```

The goal is explanatory alignment, not price prediction. ANAS asks:

```text
Which official events belong near this FX-chain stress window?
```

## Current Demo Results

General event layer:

- 100 official documents fetched locally
- 97 accepted exposure records
- 2024-2025 broad event waterfall
- impact and relevance alignment rankings

JPY case study:

- 9 official events around the 2025-11-28 to 2025-12-01 JPY stress window
- BOJ / Japan MOF / Fed official sources
- relevance and impact split for professional interpretation
- Tableau-ready case-study exports

## Repository Contents

```text
anas/                         Core package
anas/events/                  Official-event schemas, connectors, readers, agents
anas/providers/               LLM provider wrappers
scripts/                      Utility and Tableau export scripts
data/seeds/                   Public seed metadata, not raw documents
data/reference/               FrictionGraph currency/chain reference metadata
docs/                         Design docs and case-study notes
output/tableau_general_2024_2025/
                               Small derived CSVs for the general Tableau dashboard
output/tableau_jpy_case/       Small derived CSVs for the JPY case dashboard
output/cases/                  Derived case-study summaries
```

Excluded from this public upload:

- `config/api_keys.txt`
- `.env`
- raw official document JSONL files
- full runtime output directories
- private FrictionGraph raw tick data

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## API Keys

For local LLM extraction, copy one of the examples and fill only the providers you use:

```bash
cp .env.example .env
# or
cp config/api_keys.example.txt config/api_keys.txt
```

Recommended provider for this demo:

```text
TOGETHER_API_KEY
ANAS_PROVIDER=together
ANAS_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
```

Never commit real keys.

## Basic Commands

Fetch official documents from a seed file:

```bash
python3 run_events.py \
  --seed data/seeds/jpy_stress_window_seed_v1.json \
  --output-dir output/events_jpy_stress
```

Run LLM exposure extraction:

```bash
python3 run_exposure.py \
  --seed data/seeds/jpy_stress_window_seed_v1.json \
  --input output/events_jpy_stress/read_documents.jsonl \
  --output-dir output/events_jpy_stress \
  --provider together
```

Export latest accepted exposure records:

```bash
python3 run_event_latest.py --events-dir output/events_jpy_stress
```

Align exposures with FrictionGraph processed exports:

```bash
python3 run_alignment.py \
  --exposures output/events_jpy_stress/accepted_exposures_latest.json \
  --friction-daily path/to/daily_width_features_all.csv \
  --friction-chain path/to/chain_day_features_all.csv \
  --output-dir output/alignment_jpy_stress \
  --ranking-mode relevance
```

## Tableau Dashboards

The public derived CSVs are already included:

```text
output/tableau_general_2024_2025/
output/tableau_jpy_case/
```

Public Tableau dashboards:

- ANAS Alignment: `ANAS_alignment`
- JPY Stress Case Study: `JPYStressCaseStudy`

Dashboard interpretation:

- General waterfall shows where official-event pressure occurred by category/currency.
- Impact ranking emphasizes shock-like events.
- Relevance ranking emphasizes semantic fit to the currency/chain universe.
- JPY case study connects BOJ/MOF official events to the 2025-11-28 to 2025-12-01 JPY stress window.

## Design Guardrails

ANAS is designed to be safe for a public portfolio:

- official-source documents only
- no copyrighted news full-text training corpus
- strict schema validation
- fixed FrictionGraph v1 currency universe: `CAD, CHF, EUR, JPY, SGD, USD`
- optional event proxies: `CNH, XAU`
- no trading-signal or causal-prediction claim

## Notes For Reviewers

The repository demonstrates a complete event-intelligence workflow:

```text
source policy -> official retrieval -> text normalization -> LLM extraction
-> validation/judging -> derived Tableau exports -> FrictionGraph alignment
```

The code is intended as a research and portfolio demo. Full-scale production use would require larger source coverage, scheduled ingestion, stronger automated tests, persistent storage, and model monitoring.

