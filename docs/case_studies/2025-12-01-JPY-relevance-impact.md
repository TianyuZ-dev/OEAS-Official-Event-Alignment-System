# 2025-12-01 JPY Case Study: Relevance vs Impact

## Why This Version Exists

The first JPY case study exposed an important modeling issue:

```text
Some official events are highly relevant to JPY markets but have neutral or zero immediate impact.
```

The best example is the Japan Ministry of Finance foreign exchange intervention
disclosure on `2025-11-28`. The document is directly about FX intervention and
JPY market monitoring, but the disclosed intervention amount was `JPY 0`.

The old alignment formula used:

```text
currency_score * currency_impact * chain_rmsd
```

That made this event score `0`, even though it is clearly important context for
a JPY stress window.

The upgraded ANAS logic separates:

```text
relevance_score: Is this official event about this currency/theme?
impact_score: Did this event describe or imply an actual shock?
```

This is a better professional framing. It lets ANAS say:

```text
This event is highly relevant to JPY, but neutral in impact.
```

That is more useful than forcing every official event into one score.

## Code-Level Change

ANAS now keeps the old fields for compatibility:

```json
{
  "currency_score": {
    "JPY": 100
  },
  "currency_impact": {
    "JPY": 0
  }
}
```

and adds explicit relevance fields:

```json
{
  "currency_relevance": {
    "JPY": 100
  },
  "category_relevance": {
    "monetary_policy": 100
  },
  "country_relevance": {
    "JP": 100
  }
}
```

For backward compatibility, old `score` fields are treated as relevance if the
new relevance fields are absent.

## New Alignment Metrics

The alignment output now includes two separate scores.

### Relevance Alignment

```text
currency_relevance_overlap =
  sum(currency_relevance[ccy] for ccy in chain_currencies)

relevance_alignment_score =
  currency_relevance_overlap * chain_rmsd
```

This answers:

```text
Does the official event talk about the currencies that dominate the FrictionGraph chain?
```

### Impact Alignment

```text
weighted_currency_overlap =
  sum(currency_relevance[ccy] * currency_impact[ccy]
      for ccy in chain_currencies)

impact_alignment_score =
  weighted_currency_overlap * chain_rmsd
```

This answers:

```text
Does the official event describe a non-neutral shock that lines up with the chain?
```

The default impact view is still useful for shock-like events. The relevance
view is better for official monitoring, disclosure, and context events.

## Relevance Ranking Result

Using:

```text
output/alignment_jpy_stress_relevance/event_alignment_summary.csv
```

the top JPY stress-window relevance cases are:

| rank | event | window | friction date | relevance score | impact score | top alignment chain | chain RMSD rank |
| ---: | --- | --- | --- | ---: | ---: | --- | ---: |
| 1 | BOJ Noguchi speech | 7_day | 2025-12-01 | 0.061291257800 | 1.103242640400 | USD -> CHF -> JPY -> USD | 5 |
| 2 | BOJ Ueda speech | same_day | 2025-12-01 | 0.061123975020 | 0.101873291700 | USD -> SGD -> JPY -> USD | 2 |
| 3 | MOF FX intervention disclosure | next_day | 2025-12-01 | 0.039058563000 | 0.000000000000 | EUR -> SGD -> JPY -> EUR | 1 |
| 4 | MOF JGB issuance plan revision | next_day | 2025-12-01 | 0.039058563000 | 0.000000000000 | EUR -> SGD -> JPY -> EUR | 1 |

This ranking is much more interpretable than the original single-score version.
After the explicit relevance/impact rerun, the model is more conservative about
impact than the first compatibility pass. That is useful: the relevance view
still identifies the correct JPY official-event neighborhood, while the impact
view only gives nonzero credit when the document contains stronger shock-like
content.

## The Key Improvement: MOF FX Intervention Disclosure

Official source:

[Japan Ministry of Finance: Foreign Exchange Intervention Operations](https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20251128e.html)

The event:

```text
event_id: mof_2025_11_28_fx_intervention_operations
event_date: 2025-11-28
document: Foreign Exchange Intervention Operations
period covered: October 30, 2025 through November 26, 2025
disclosed intervention amount: JPY 0
```

ANAS exposure:

```json
{
  "currency_relevance": {
    "JPY": 100,
    "USD": 0,
    "EUR": 0,
    "CHF": 0
  },
  "currency_impact": {
    "JPY": 0,
    "USD": 0,
    "EUR": 0,
    "CHF": 0
  },
  "currency_direction": {
    "JPY": 0,
    "USD": 0,
    "EUR": 0,
    "CHF": 0
  }
}
```

Interpretation:

```text
High relevance:
  The document is directly about FX intervention operations.

Neutral impact:
  The official disclosed amount is JPY 0.

Correct ANAS behavior:
  Include the event as a relevant JPY monitoring context.
  Do not treat it as an active intervention shock.
```

This is exactly why relevance and impact should be separated.

## MOF FX Event Alignment

Same-day relevance alignment:

```text
event_id: mof_2025_11_28_fx_intervention_operations
window: same_day
friction_date: 2025-11-28
top_alignment_chain: JPY -> CHF -> CAD -> JPY
top_alignment_chain_rmsd_rank: 1
relevance_alignment_score: 0.023172249600
impact_alignment_score: 0.000000000000
```

Next-day relevance alignment:

```text
window: next_day
friction_date: 2025-12-01
top_alignment_chain: EUR -> SGD -> JPY -> EUR
top_alignment_chain_rmsd_rank: 1
relevance_alignment_score: 0.039058563000
impact_alignment_score: 0.000000000000
```

This is the exact behavior we want:

```text
The event sits on the correct JPY-heavy chains.
The chains are high-ranked by FrictionGraph RMSD.
The event has zero impact because the official intervention amount was zero.
```

## BOJ Ueda Speech: High Relevance and Conservative Impact

Official source:

[Bank of Japan: Japan's Economy and Monetary Policy](https://www.boj.or.jp/en/about/press/koen_2025/ko251201a.htm)

The BOJ Governor Ueda speech is the cleanest same-day relevance case. After the
explicit rerun, the model treats it as highly relevant to JPY and Japan monetary
policy, but conservative on immediate impact:

```text
event_id: boj_2025_12_01_ueda_nagoya_speech
window: same_day
friction_date: 2025-12-01
top_alignment_chain: USD -> SGD -> JPY -> USD
top_alignment_chain_rmsd_rank: 2
relevance_alignment_score: 0.061123975020
impact_alignment_score: 0.101873291700
```

ANAS exposure:

```json
{
  "category_relevance": {
    "monetary_policy": 90,
    "macro_growth": 80,
    "inflation": 70,
    "trade_policy": 60
  },
  "currency_relevance": {
    "JPY": 100,
    "USD": 60,
    "EUR": 20,
    "SGD": 20,
    "CHF": 20
  },
  "currency_impact": {
    "JPY": 0,
    "USD": 5,
    "EUR": 0,
    "SGD": 0,
    "CHF": 0
  }
}
```

Interpretation:

```text
The BOJ speech is directly about Japanese monetary policy.
ANAS assigns high JPY relevance, but conservatively avoids calling the speech an immediate JPY shock.
The strongest aligned chain is the second-largest RMSD chain on 2025-12-01.
```

This is the cleanest same-day "high relevance" case. Its low impact score is a
feature, not a failure: the system is separating official relevance from a
strong directional shock claim.

## MOF JGB Issuance Revision: Rates Channel

Official source:

[Japan Ministry of Finance: JGB Issuance Plan](https://www.mof.go.jp/english/policy/jgbs/debt_management/plan/index.htm)

The JGB issuance revision remains relevant to JPY and Japan rates, but after
the explicit rerun the model treats the indexed page as a reference/disclosure
record rather than a realized shock:

```text
event_id: mof_2025_11_28_jgb_issuance_plan_revision
window: next_day
friction_date: 2025-12-01
top_alignment_chain: EUR -> SGD -> JPY -> EUR
top_alignment_chain_rmsd_rank: 1
relevance_alignment_score: 0.039058563000
impact_alignment_score: 0.000000000000
```

This event is not as pure as the BOJ speeches, but it still gives ANAS a
rates/fiscal relevance channel:

```text
JGB supply / fiscal issuance
  -> Japan rates expectations
  -> JPY-linked FrictionGraph chains
```

The conservative impact result also tells us something operational: for indexed
official pages, ANAS may need a deeper attachment-level connector to extract the
actual revised issuance table before assigning a nonzero impact score.

## Why This Is Better Than The Single-Score Version

The previous single-score view was good for shock-like events, but it blurred
three different concepts:

```text
1. Is the event about JPY?
2. Does the event have directional content?
3. Does the event imply a market-structure shock?
```

The new version separates them:

| concept | field | example |
| --- | --- | --- |
| event relevance | `currency_relevance` | MOF FX disclosure has JPY relevance 100 |
| directional view | `currency_direction` | MOF FX disclosure has JPY direction 0 |
| impact / shock | `currency_impact` | MOF FX disclosure has JPY impact 0 |
| market-side strength | `chain_rmsd` | 2025-12-01 top JPY chain RMSD is large |

This makes the system easier to explain in interviews:

```text
ANAS does not force every official event to be a shock.
It can distinguish monitoring relevance from market impact.
```

## Tableau Implication

For Tableau, use two views:

### Relevance View

Use:

```text
output/alignment_jpy_stress_relevance/event_alignment_summary.csv
output/alignment_jpy_stress_relevance/event_chain_alignment.csv
```

Fields:

```text
relevance_alignment_score
currency_relevance_overlap
chain_rank_by_relevance_alignment
```

Purpose:

```text
Show which official events belong near the JPY stress window.
```

### Impact View

Use:

```text
output/alignment_jpy_stress/event_alignment_summary.csv
output/alignment_jpy_stress/event_chain_alignment.csv
```

Fields:

```text
impact_alignment_score
weighted_currency_overlap
chain_rank_by_impact_alignment
```

Purpose:

```text
Show which relevant official events also carry non-neutral event impact.
```

Together, the two views create a cleaner dashboard:

```text
left: official-event relevance
middle: impact / shock strength
right: FrictionGraph chain RMSD response
```

## Portfolio Language

Use this wording:

```text
The upgraded ANAS struct separates official-event relevance from event impact.
In the JPY stress case, MOF FX intervention disclosure ranks high on relevance
but zero on impact, while BOJ monetary-policy communication ranks high on
relevance and receives a conservative nonzero impact score only where the
document supports it. This distinction makes the alignment layer more auditable
and prevents neutral official disclosures or speeches from being mislabeled as
shocks.
```

Avoid:

```text
ANAS proves that these official events caused the JPY move.
ANAS predicts the yen.
The MOF zero-intervention disclosure caused the spike.
```

## Reproduction Commands

The explicit relevance/impact rerun used:

```bash
python3 run_exposure.py \
  --seed data/seeds/jpy_stress_window_seed_v1.json \
  --input output/events_jpy_stress/read_documents.jsonl \
  --output-dir output/events_jpy_stress \
  --provider together \
  --force
```

Then both alignment views were regenerated:

```bash
python3 run_event_latest.py \
  --events-dir output/events_jpy_stress

python3 run_alignment.py \
  --exposures output/events_jpy_stress/accepted_exposures_latest.json \
  --output-dir output/alignment_jpy_stress \
  --ranking-mode impact

python3 run_alignment.py \
  --exposures output/events_jpy_stress/accepted_exposures_latest.json \
  --output-dir output/alignment_jpy_stress_relevance \
  --ranking-mode relevance
```

This makes the JSON outputs fully explicit rather than relying on the
backward-compatible interpretation of `score` as relevance.
