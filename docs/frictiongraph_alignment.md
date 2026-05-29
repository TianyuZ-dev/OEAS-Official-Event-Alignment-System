# ANAS x FrictionGraph Alignment Design

This document defines how ANAS event signals align with FrictionGraph's daily FX
market-structure outputs.

The key idea is not simple date overlap. The alignment unit is:

```text
event country/currency exposure
  x
FrictionGraph FX chain currency composition
  x
daily friction response strength
```

## FrictionGraph Role

FrictionGraph is the market-side screen. It detects when FX market structure
becomes internally inconsistent through triangular currency friction.

Relevant processed outputs include:

```json
{
  "date": "YYYY-MM-DD",
  "sum_rmsd": 0.0,
  "gap": 0.0,
  "top_chain": "JPY-SGD-CHF",
  "chain_rmsd": 0.0,
  "is_peak": true
}
```

ANAS should not require raw tick data for the public demo. It should consume
FrictionGraph's processed daily outputs only.

## Currency And Chain Universe

ANAS must use the same currency and chain universe as FrictionGraph.

First implementation rule:

```text
Do not hand-write the chain/currency list.
Extract it from FrictionGraph's actual processed files and chain vocabulary.
```

Expected extraction logic:

1. Read FrictionGraph processed chain or pair exports.
2. Parse every currency pair or triangular chain.
3. Split instruments into ISO-style currency codes.
4. Deduplicate and sort into a stable order.
5. Save the universe and chain vocabulary in `data/reference/`.

Example structure:

```json
{
  "version": "frictiongraph_v1",
  "source": "extracted_from_frictiongraph_processed_outputs",
  "chain_currencies": ["CAD", "CHF", "EUR", "JPY", "SGD", "USD"],
  "triangle_chain_count": 32
}
```

The example above is not the final universe. The final list must come from the
actual FrictionGraph data.

### Current Extraction Result

The current local FrictionGraph processed exports were read from:

```text
data/frictiongraph/
```

Reference files generated in ANAS:

```text
data/reference/frictiongraph_universe.json
data/reference/frictiongraph_chains.json
data/reference/frictiongraph_chains.csv
```

Important result:

```text
FrictionGraph currently has 32 triangle chains, not 32 currencies.
```

Current processed chain universe:

```text
CAD, CHF, EUR, JPY, SGD, USD
```

Current configured instrument currency/proxy universe:

```text
CAD, CHF, CNH, EUR, JPY, SGD, USD, XAU
```

For ANAS v1, chain alignment should use the 6 chain currencies. Event exposure
can still include `CNH` and `XAU` as configured proxy instruments, but they will
not directly overlap a triangular chain unless FrictionGraph later exports
chains containing them.

## Currency to Country / Region Mapping

Currency exposure is not identical to country exposure. Some currencies represent
single countries, some represent regions, and some act as market proxies.

ANAS should maintain a reference mapping:

```json
{
  "USD": {
    "region_label": "United States",
    "country_codes": ["US"],
    "roles": ["reserve_currency", "safe_haven", "trade_invoice"]
  },
  "EUR": {
    "region_label": "Euro Area",
    "country_codes": ["EU", "DE", "FR", "IT", "ES", "NL"],
    "roles": ["regional_currency", "europe_growth", "risk_currency"]
  },
  "CHF": {
    "region_label": "Switzerland",
    "country_codes": ["CH"],
    "roles": ["safe_haven"]
  },
  "SGD": {
    "region_label": "Singapore",
    "country_codes": ["SG"],
    "roles": ["asia_trade_hub", "china_proxy_partial"]
  }
}
```

This mapping should be reviewed manually after the FrictionGraph chain and proxy
currency universe is extracted.

## Event Exposure Layers

ANAS produces three exposure layers for each official event.

### 1. Category Exposure

Fixed 16-category taxonomy:

```text
0  macro_growth
1  monetary_policy
2  inflation
3  fiscal_policy
4  geopolitics
5  trade_policy
6  sanctions
7  energy_oil_gas
8  commodities_metals
9  semiconductors
10 artificial_intelligence
11 supply_chain
12 defense_security
13 elections_policy
14 equities_risk
15 crypto_digital_assets
```

For each category:

```text
score      0 to 100
direction -100 to 100
impact    0 to 100
```

### 2. Country / Region Exposure

Country exposure captures the event's direct geopolitical or economic target.

Examples:

- U.S. tariff update: US, China, EU, Mexico, Canada
- OFAC sanctions: sanctioning country, sanctioned country, affected region
- oil supply disruption: producer country, importer regions, transit chokepoints
- chip export controls: US, China, Taiwan, Netherlands, Japan, South Korea

Country exposure is useful for interpretation, but currency exposure is the
primary bridge to FrictionGraph.

### 3. Currency Exposure

Currency exposure maps event impact into FrictionGraph's 6 chain currencies and
optional configured proxy instruments.

Examples:

```text
US-China trade escalation
  direct: USD, CNH proxy
  chain/proxy exposure: SGD, JPY, CHF

oil supply shock
  chain exposure: CAD, USD, CHF, JPY

European energy stress
  chain exposure: EUR, CHF, USD

chip / AI export controls
  direct/proxy: USD, CNH proxy
  chain exposure: SGD, JPY, CHF

safe-haven geopolitical shock
  direct/proxy: USD, CHF, JPY, XAU proxy
```

These examples are priors. The LLM extractor proposes exposure, and later
manual review or rule-based calibration can improve it.

## Daily Aggregation

ANAS v1 uses daily granularity because FrictionGraph's public demo outputs are
daily.

Multiple events on the same date are aggregated into one daily exposure vector.

For a currency or category dimension `k`:

```text
daily_direction[k] =
  sum(direction[event, k] * impact[event, k])
  /
  max(sum(impact[event, k]), 1)

daily_impact[k] =
  max(impact[event, k])

daily_score[k] =
  max(score[event, k])
```

This keeps strong event signals visible without letting many weak events dilute
the day.

## Friction Response Layer

FrictionGraph daily response should include both broad day-level features and
chain-level features.

Day-level features:

```json
{
  "date": "YYYY-MM-DD",
  "sum_rmsd": 0.0,
  "gap": 0.0,
  "is_peak": false,
  "peak_rank": 0
}
```

Chain-level features:

```json
{
  "date": "YYYY-MM-DD",
  "chain": "JPY-SGD-CHF",
  "chain_currencies": ["JPY", "SGD", "CHF"],
  "chain_rmsd": 0.0,
  "chain_rank_by_rmsd": 1
}
```

If FrictionGraph exports only a top chain per day in the first version, ANAS can
start with that. Later versions should use all chain-day rows.

The first implementation should not invent a separate chain contribution ratio.
The contribution view is the ranking of each separated chain's own `rmsd` on
that day. In other words, the most important market-side chain is:

```text
top_rmsd_chain = chain with rank_by_rmsd == 1 for the selected date
```

This is intentionally distinct from the top event-aligned chain. A chain can
have the largest standalone FrictionGraph response while a different chain has
the strongest overlap with the event's currency exposure.

## Alignment Score

For event `e`, date window `w`, and FrictionGraph chain `c`:

```text
currency_overlap(e, c) =
  sum(currency_score[e, ccy] * currency_impact[e, ccy]
      for ccy in chain_currencies[c])

directional_overlap(e, c) =
  sum(abs(currency_direction[e, ccy]) * currency_impact[e, ccy]
      for ccy in chain_currencies[c])

alignment_score(e, c, w) =
  normalized_event_impact(e)
  * normalized_currency_overlap(e, c)
  * normalized_chain_response(c, w)
```

For demo readability, the first implementation can use:

```text
simple_alignment_score =
  sum(currency_score[ccy] * currency_impact[ccy] for ccy in chain_currencies)
  * chain_rmsd
```

Scores are for ranking and explanation, not trading decisions.

## Daily Windows

The first version uses daily windows:

```text
same_day
next_day
3_day
7_day
```

Definitions:

```text
same_day: event_date
next_day: first available FrictionGraph date after event_date
3_day: max response over event_date through event_date + 3 calendar days
7_day: max response over event_date through event_date + 7 calendar days
```

If a date is missing from FrictionGraph outputs, skip it rather than imputing in
the first demo.

## Waterfall Views

The target demo has three stacked waterfall views.

### 1. Category Waterfall

```text
date x 16 ANAS categories
color: daily_direction
intensity: daily_impact
```

Purpose: show which event themes dominated each day.

### 2. Currency Exposure Waterfall

```text
date x 6 FrictionGraph chain currencies, plus optional CNH/XAU proxy exposure
color: currency_direction
intensity: currency_impact
```

Purpose: show where official event pressure points in currency space.

### 3. Friction Response Waterfall

```text
date x 32 FX triangle chains or chain family
color/intensity: chain_rmsd or normalized width
```

Purpose: show where market structure actually widened.

## Case Study Template

Each case should be explainable in a compact record:

```json
{
  "case_id": "chip_export_controls_2025_...",
  "event_summary": "Official export-control update affecting advanced chips and AI compute.",
  "dominant_categories": ["trade_policy", "semiconductors", "artificial_intelligence", "geopolitics"],
  "dominant_currencies": ["USD", "SGD", "JPY", "CHF"],
  "friction_response": {
    "date": "YYYY-MM-DD",
    "top_chain": "JPY-SGD-CHF",
    "chain_rmsd": 0.0,
    "is_peak": true
  },
  "interpretation": "The official event's Asia technology/trade exposure overlaps with the day's high-friction FX chain."
}
```

## First Demo Acceptance Criteria

The first 10-event demo is successful if it can show:

- a stable FrictionGraph 6-currency chain universe and 32-chain vocabulary extracted from processed data
- 10 official events with source policies and provenance
- ANAS exposure structs for those events
- daily aggregated category and currency vectors
- at least one readable alignment case with chain overlap
- waterfall-ready CSV/JSON outputs

It does not need to prove statistical predictability.
