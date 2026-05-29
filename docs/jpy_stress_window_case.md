# JPY Stress Window Case

This document defines the ANAS v1 core case study built around a clear
FrictionGraph stress window dominated by JPY-heavy FX triangle chains.

## Core Question

Can ANAS identify official-event exposure that aligns more strongly with a
known JPY-heavy FrictionGraph stress window than unrelated event exposure?

This is an explanatory alignment task, not a causality or trading-signal claim.

## FrictionGraph Stress Window

Primary stress dates:

```text
2025-11-28
2025-12-01
```

Event search window:

```text
2025-11-15 through 2025-12-15
```

The search window intentionally includes pre-window official communication and
post-window confirmation/context.

## Observed FrictionGraph Pattern

On 2025-11-28, the largest chain-level RMSD rows were concentrated in
JPY-heavy chains, especially JPY/CHF/CAD and JPY/CHF/SGD structures.

On 2025-12-01, the signal broadened across JPY chains involving EUR, SGD, USD,
CHF, and CAD. This makes the case stronger than a single-pair move: the stress
appears across multiple triangular paths containing JPY.

Interpretation goal:

```text
FrictionGraph detects abnormal JPY-chain market-structure stress.
ANAS searches official events around the window.
JPY/Japan/monetary/FX-relevant events should rank higher than unrelated controls.
```

## Event Groups

### Group A: JPY / Japan / BOJ / MOF / FX / Rates

These are expected to have the strongest direct alignment with JPY-heavy chains.

Candidate official sources:

- Bank of Japan
- Japan Ministry of Finance
- Japan Cabinet Office
- Japan Statistics Bureau
- Japanese government press conferences or official releases
- Federal Reserve / FOMC if USD-JPY rate channel is central

### Group B: Global Macro / USD / Risk

These may affect JPY indirectly through risk appetite, rates, or USD funding.

Candidate official sources:

- Federal Reserve
- U.S. Treasury
- BLS / BEA
- IMF / BIS / OECD
- major official trade or sanctions releases

### Group C: Unrelated Controls

These should be included to make the demo more credible. They may be real
official events in the same period, but they should have weak or indirect JPY
exposure.

Candidate types:

- non-Japan domestic policy events
- sector-specific events without FX/rates relevance
- non-JPY commodity or technology releases

## Expected Demo Result

The case is successful if ANAS shows:

```text
Group A alignment score > Group B alignment score > Group C alignment score
```

The exact ordering does not need to be perfect for every event. The goal is a
readable ranking where JPY/Japan/monetary events are visibly more aligned with
JPY-heavy FrictionGraph chains than unrelated controls.

## Required Outputs

Seed file:

```text
data/seeds/jpy_stress_window_seed_v1.json
```

Event fetch/exposure outputs:

```text
output/events_jpy_stress/
```

Alignment outputs:

```text
output/alignment_jpy_stress/
```

Case-study outputs:

```text
output/cases/jpy_stress_window_v1.md
output/cases/jpy_stress_window_v1.json
output/cases/jpy_stress_window_v1.csv
```

## Candidate Events v0

The first search pass found the following official-source candidates. This list
should become the basis for `data/seeds/jpy_stress_window_seed_v1.json` after a
manual review pass.

### Group A: Direct JPY / Japan / BOJ / MOF / FX / Rates Candidates

| event_date | event_id | source | title | why it matters |
| --- | --- | --- | --- | --- |
| 2025-11-27 | `boj_2025_11_27_noguchi_oita_speech` | Bank of Japan | Economic Activity, Prices, and Monetary Policy in Japan | BOJ Policy Board speech one day before the 2025-11-28 JPY-heavy stress date. Direct Japan monetary-policy exposure. |
| 2025-11-28 | `mof_2025_11_28_fx_intervention_operations` | Japan Ministry of Finance | Foreign Exchange Intervention Operations (October 30, 2025 through November 26, 2025) | Direct official FX/intervention disclosure on the first stress date. Even a zero intervention result is highly relevant to JPY market interpretation. |
| 2025-11-28 | `mof_2025_11_28_jgb_issuance_plan_revision` | Japan Ministry of Finance | FY2025 JGB Issuance Plan, revised in November supplementary budget | JGB supply and fiscal financing can affect Japan rates, term premia, and JPY-linked chains. |
| 2025-12-01 | `boj_2025_12_01_ueda_nagoya_speech` | Bank of Japan | Japan's Economy and Monetary Policy | BOJ Governor speech on the second stress date, explicitly tied to the next Monetary Policy Meeting and wage/inflation information gathering. |
| 2025-12-05 | `mof_2025_12_05_international_reserves` | Japan Ministry of Finance | International Reserves / Foreign Currency Liquidity as of end-November 2025 | FX reserve disclosure shortly after the stress window. Useful for JPY/USD reserve and official liquidity context. |
| 2025-12-10 | `boj_2025_12_10_cgpi_november` | Bank of Japan | Corporate Goods Price Index, November 2025 | Japan inflation pipeline data, relevant to BOJ policy expectations and JPY rates channel. |

### Group B: Indirect Global Macro / USD / Risk Candidates

| event_date | event_id | source | title | why it matters |
| --- | --- | --- | --- | --- |
| 2025-11-17 | `cao_2025_11_17_japan_gdp_q3_first_prelim` | Japan Cabinet Office / ESRI | Quarterly Estimates of GDP for Jul.-Sep. 2025, first preliminary | Japan macro growth signal before the stress window. Relevant but less directly FX-specific than BOJ/MOF events. |
| 2025-12-08 | `cao_2025_12_08_japan_gdp_q3_second_prelim` | Japan Cabinet Office / ESRI | Quarterly Estimates of GDP for Jul.-Sep. 2025, second preliminary | Japan macro confirmation after the stress window. Useful as context, but timing is post-window. |
| 2025-12-10 | `fed_2025_12_10_fomc_statement` | Federal Reserve | Federal Reserve issues FOMC statement | USD rates event that may affect USD/JPY and global risk channels, but not Japan-specific. |

### Group C: Control Candidates

| event_date | event_id | source | title | why it matters |
| --- | --- | --- | --- | --- |
| 2025-12-02 | `cao_2025_12_02_consumer_confidence_november` | Japan Cabinet Office / ESRI | Consumer Confidence Survey, November 2025 | Japan domestic sentiment. It may have macro relevance but should be weaker than direct BOJ/MOF/FX events. |
| 2025-12-11 | `cao_2025_12_11_business_outlook_q4` | Japan Cabinet Office / ESRI | Business Outlook Survey, October-December 2025 | Domestic business sentiment/control event after the stress window. |

## First Seed Recommendation

For the first executable seed, use 8 to 10 events:

```text
Core A events:
  BOJ Noguchi speech, MOF FX intervention operations, BOJ Ueda speech

Supporting A/B events:
  MOF JGB issuance revision, MOF reserves, Japan GDP first preliminary, Fed FOMC

Controls:
  Japan consumer confidence, Japan business outlook, or another official but weakly FX-linked event
```

The strongest expected case is:

```text
2025-12-01 BOJ Governor Ueda speech
  x
2025-12-01 JPY-heavy FrictionGraph chain response
```

The strongest first-stress-date case is:

```text
2025-11-28 MOF foreign exchange intervention operations disclosure
  x
2025-11-28 JPY-heavy FrictionGraph chain response
```

## Portfolio Language

Use:

```text
ANAS links official-event exposure to nearby FrictionGraph chain behavior.
The JPY stress window shows that JPY-relevant official events rank higher
against JPY-heavy FX chains than unrelated controls.
```

Avoid:

```text
ANAS proves the event caused the JPY move.
ANAS predicts JPY.
This is a trading signal.
```
