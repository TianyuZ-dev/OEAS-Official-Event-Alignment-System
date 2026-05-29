# JPY Stress Window v1

These cases connect license-safe official event records to FrictionGraph's processed FX chain outputs.
They are designed for explanation, Tableau annotation, and portfolio review, not prediction claims.

## 1. Economic Activity, Prices, and Monetary Policy in Japan

- Event ID: `boj_2025_11_27_noguchi_oita_speech`
- Event date: `2025-11-27`
- Source: Bank of Japan
- Official URL: https://www.boj.or.jp/en/about/press/koen_2025/ko251127a.htm
- Selected window: `7_day` ending on `2025-12-01`
- Daily sum RMSD: `0.004020865281`
- Ranking mode: `impact`
- Top RMSD chain: `EUR -> SGD -> JPY -> EUR`
- Top event-alignment chain: `USD -> SGD -> JPY -> USD`
- Top alignment chain RMSD rank: `2`
- Alignment score: `1.222479500400`
- Relevance alignment score: `0.061123975020`
- Impact alignment score: `1.222479500400`

### Dominant Categories

- `monetary_policy` score=90, impact=40, direction=20
- `macro_growth` score=80, impact=20, direction=10
- `inflation` score=80, impact=20, direction=10
- `trade_policy` score=60, impact=20, direction=-20
- `artificial_intelligence` score=40, impact=20, direction=20

### Dominant Currencies

- `JPY` score=100, impact=20, direction=10
- `USD` score=80, impact=20, direction=-10
- `CHF` score=20, impact=0, direction=0
- `EUR` score=20, impact=0, direction=0

### Interpretation

The official event is represented by ANAS as a monetary_policy, macro_growth, inflation, trade_policy exposure with currency pressure around JPY, USD, CHF, EUR. In the 7_day window, FrictionGraph's largest standalone RMSD chain is EUR -> SGD -> JPY -> EUR, while the strongest event-overlap chain is USD -> SGD -> JPY -> USD. These are different chains, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment_jpy_stress/event_alignment_summary.csv`
- `output/alignment_jpy_stress/event_chain_alignment.csv`
- `output/alignment_jpy_stress/waterfall_category_daily.csv`
- `output/alignment_jpy_stress/waterfall_currency_daily.csv`

## 2. Federal Reserve Issues FOMC Statement

- Event ID: `fed_2025_12_10_fomc_statement`
- Event date: `2025-12-10`
- Source: Federal Reserve Board
- Official URL: https://www.federalreserve.gov/newsevents/pressreleases/monetary20251210a.htm
- Selected window: `next_day` ending on `2025-12-11`
- Daily sum RMSD: `0.000995739334`
- Ranking mode: `impact`
- Top RMSD chain: `EUR -> SGD -> CHF -> EUR`
- Top event-alignment chain: `USD -> SGD -> CHF -> USD`
- Top alignment chain RMSD rank: `2`
- Alignment score: `0.465037976000`
- Relevance alignment score: `0.006975569640`
- Impact alignment score: `0.465037976000`

### Dominant Categories

- `monetary_policy` score=100, impact=80, direction=-25
- `inflation` score=90, impact=60, direction=-20
- `macro_growth` score=80, impact=40, direction=20
- `equities_risk` score=60, impact=40, direction=30

### Dominant Currencies

- `USD` score=100, impact=80, direction=-15
- `JPY` score=20, impact=20, direction=5
- `CHF` score=10, impact=0, direction=0
- `EUR` score=10, impact=0, direction=0
- `SGD` score=10, impact=0, direction=0

### Interpretation

The official event is represented by ANAS as a monetary_policy, inflation, macro_growth, equities_risk exposure with currency pressure around USD, JPY, CHF, EUR. In the next_day window, FrictionGraph's largest standalone RMSD chain is EUR -> SGD -> CHF -> EUR, while the strongest event-overlap chain is USD -> SGD -> CHF -> USD. These are different chains, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment_jpy_stress/event_alignment_summary.csv`
- `output/alignment_jpy_stress/event_chain_alignment.csv`
- `output/alignment_jpy_stress/waterfall_category_daily.csv`
- `output/alignment_jpy_stress/waterfall_currency_daily.csv`

## 3. Japan's Economy and Monetary Policy

- Event ID: `boj_2025_12_01_ueda_nagoya_speech`
- Event date: `2025-12-01`
- Source: Bank of Japan
- Official URL: https://www.boj.or.jp/en/about/press/koen_2025/ko251201a.htm
- Selected window: `same_day` ending on `2025-12-01`
- Daily sum RMSD: `0.004020865281`
- Ranking mode: `impact`
- Top RMSD chain: `EUR -> SGD -> JPY -> EUR`
- Top event-alignment chain: `USD -> SGD -> JPY -> USD`
- Top alignment chain RMSD rank: `2`
- Alignment score: `0.101873291700`
- Relevance alignment score: `0.061123975020`
- Impact alignment score: `0.101873291700`

### Dominant Categories

- `monetary_policy` score=100, impact=0, direction=0
- `macro_growth` score=80, impact=10, direction=20
- `inflation` score=60, impact=5, direction=10
- `artificial_intelligence` score=40, impact=10, direction=20
- `trade_policy` score=40, impact=5, direction=-10

### Dominant Currencies

- `JPY` score=100, impact=0, direction=0
- `USD` score=60, impact=5, direction=10
- `CHF` score=20, impact=0, direction=0
- `EUR` score=20, impact=0, direction=0
- `SGD` score=20, impact=0, direction=0

### Interpretation

The official event is represented by ANAS as a monetary_policy, macro_growth, inflation, trade_policy exposure with currency pressure around JPY, USD, CHF, EUR. In the same_day window, FrictionGraph's largest standalone RMSD chain is EUR -> SGD -> JPY -> EUR, while the strongest event-overlap chain is USD -> SGD -> JPY -> USD. These are different chains, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment_jpy_stress/event_alignment_summary.csv`
- `output/alignment_jpy_stress/event_chain_alignment.csv`
- `output/alignment_jpy_stress/waterfall_category_daily.csv`
- `output/alignment_jpy_stress/waterfall_currency_daily.csv`

## 4. Foreign Exchange Intervention Operations (October 30, 2025 through November 26, 2025)

- Event ID: `mof_2025_11_28_fx_intervention_operations`
- Event date: `2025-11-28`
- Source: Japan Ministry of Finance
- Official URL: https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20251128e.html
- Selected window: `next_day` ending on `2025-12-01`
- Daily sum RMSD: `0.004020865281`
- Ranking mode: `impact`
- Top RMSD chain: `EUR -> SGD -> JPY -> EUR`
- Top event-alignment chain: `EUR -> SGD -> JPY -> EUR`
- Top alignment chain RMSD rank: `1`
- Alignment score: `0.000000000000`
- Relevance alignment score: `0.039058563000`
- Impact alignment score: `0.000000000000`

### Dominant Categories

- `monetary_policy` score=100, impact=0, direction=0
- `macro_growth` score=20, impact=0, direction=0
- `geopolitics` score=20, impact=0, direction=0

### Dominant Currencies

- `JPY` score=100, impact=0, direction=0

### Interpretation

The official event is represented by ANAS as a monetary_policy, macro_growth, geopolitics exposure with currency pressure around JPY. In the next_day window, FrictionGraph's largest standalone RMSD chain is EUR -> SGD -> JPY -> EUR, while the strongest event-overlap chain is EUR -> SGD -> JPY -> EUR. These are same chain, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment_jpy_stress/event_alignment_summary.csv`
- `output/alignment_jpy_stress/event_chain_alignment.csv`
- `output/alignment_jpy_stress/waterfall_category_daily.csv`
- `output/alignment_jpy_stress/waterfall_currency_daily.csv`

## 5. FY2025 JGB Issuance Plan, Revised in November Supplementary Budget

- Event ID: `mof_2025_11_28_jgb_issuance_plan_revision`
- Event date: `2025-11-28`
- Source: Japan Ministry of Finance
- Official URL: https://www.mof.go.jp/english/policy/jgbs/debt_management/plan/index.htm
- Selected window: `next_day` ending on `2025-12-01`
- Daily sum RMSD: `0.004020865281`
- Ranking mode: `impact`
- Top RMSD chain: `EUR -> SGD -> JPY -> EUR`
- Top event-alignment chain: `EUR -> SGD -> JPY -> EUR`
- Top alignment chain RMSD rank: `1`
- Alignment score: `0.000000000000`
- Relevance alignment score: `0.039058563000`
- Impact alignment score: `0.000000000000`

### Dominant Categories

- `fiscal_policy` score=100, impact=0, direction=0
- `monetary_policy` score=80, impact=0, direction=0
- `macro_growth` score=20, impact=0, direction=0

### Dominant Currencies

- `JPY` score=100, impact=0, direction=0

### Interpretation

The official event is represented by ANAS as a fiscal_policy, monetary_policy, macro_growth exposure with currency pressure around JPY. In the next_day window, FrictionGraph's largest standalone RMSD chain is EUR -> SGD -> JPY -> EUR, while the strongest event-overlap chain is EUR -> SGD -> JPY -> EUR. These are same chain, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment_jpy_stress/event_alignment_summary.csv`
- `output/alignment_jpy_stress/event_chain_alignment.csv`
- `output/alignment_jpy_stress/waterfall_category_daily.csv`
- `output/alignment_jpy_stress/waterfall_currency_daily.csv`

## 6. International Reserves / Foreign Currency Liquidity as of the End of November 2025

- Event ID: `mof_2025_12_05_international_reserves`
- Event date: `2025-12-05`
- Source: Japan Ministry of Finance
- Official URL: https://www.mof.go.jp/english/policy/international_policy/reference/official_reserve_assets/e0711.html
- Selected window: `7_day` ending on `2025-12-10`
- Daily sum RMSD: `0.001181501814`
- Ranking mode: `impact`
- Top RMSD chain: `EUR -> SGD -> CHF -> EUR`
- Top event-alignment chain: `EUR -> SGD -> CHF -> EUR`
- Top alignment chain RMSD rank: `1`
- Alignment score: `0.000000000000`
- Relevance alignment score: `0.000000000000`
- Impact alignment score: `0.000000000000`

### Dominant Categories

- `monetary_policy` score=100, impact=10, direction=10
- `macro_growth` score=20, impact=0, direction=0
- `commodities_metals` score=20, impact=0, direction=0

### Dominant Currencies

- `JPY` score=100, impact=0, direction=0
- `USD` score=100, impact=0, direction=0
- `XAU` score=20, impact=0, direction=0

### Interpretation

The official event is represented by ANAS as a monetary_policy, macro_growth, commodities_metals exposure with currency pressure around JPY, USD, XAU. In the 7_day window, FrictionGraph's largest standalone RMSD chain is EUR -> SGD -> CHF -> EUR, while the strongest event-overlap chain is EUR -> SGD -> CHF -> EUR. These are same chain, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment_jpy_stress/event_alignment_summary.csv`
- `output/alignment_jpy_stress/event_chain_alignment.csv`
- `output/alignment_jpy_stress/waterfall_category_daily.csv`
- `output/alignment_jpy_stress/waterfall_currency_daily.csv`
