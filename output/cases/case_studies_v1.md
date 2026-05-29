# ANAS Case Studies v1

These cases connect license-safe official event records to FrictionGraph's processed FX chain outputs.
They are designed for explanation, Tableau annotation, and portfolio review, not prediction claims.

## 1. USTR Finalizes Action on China Tariffs Following Statutory Four-Year Review

- Event ID: `ustr_2024_09_13_china_section_301_tariffs`
- Event date: `2024-09-13`
- Source: Office of the U.S. Trade Representative
- Official URL: https://ustr.gov/about-us/policy-offices/press-office/press-releases/2024/september/ustr-finalizes-action-china-tariffs-following-statutory-four-year-review
- Selected window: `7_day` ending on `2024-09-18`
- Daily sum RMSD: `0.002466967755`
- Top RMSD chain: `EUR -> JPY -> SGD -> EUR`
- Top event-alignment chain: `USD -> JPY -> SGD -> USD`
- Top alignment chain RMSD rank: `8`
- Alignment score: `1.371784563600`

### Dominant Categories

- `trade_policy` score=100, impact=100, direction=-100
- `geopolitics` score=80, impact=80, direction=-80
- `supply_chain` score=80, impact=80, direction=-80
- `semiconductors` score=60, impact=60, direction=-60
- `commodities_metals` score=40, impact=20, direction=-40

### Dominant Currencies

- `USD` score=100, impact=100, direction=100
- `CNH` score=100, impact=100, direction=-100
- `JPY` score=40, impact=40, direction=-40
- `SGD` score=40, impact=40, direction=-40
- `CHF` score=20, impact=20, direction=20

### Interpretation

The official event is represented by ANAS as a trade_policy, geopolitics, supply_chain, semiconductors exposure with currency pressure around USD, CNH, JPY, SGD. In the 7_day window, FrictionGraph's largest standalone RMSD chain is EUR -> JPY -> SGD -> EUR, while the strongest event-overlap chain is USD -> JPY -> SGD -> USD. These are different chains, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment/event_alignment_summary.csv`
- `output/alignment/event_chain_alignment.csv`
- `output/alignment/waterfall_category_daily.csv`
- `output/alignment/waterfall_currency_daily.csv`

## 2. President Donald J. Trump Declares National Emergency to Increase our Competitive Edge, Protect our Sovereignty, and Strengthen our National and Economic Security

- Event ID: `whitehouse_2025_04_02_reciprocal_tariffs`
- Event date: `2025-04-02`
- Source: White House
- Official URL: https://www.whitehouse.gov/fact-sheets/2025/04/fact-sheet-president-donald-j-trump-declares-national-emergency-to-increase-our-competitive-edge-protect-our-sovereignty-and-strengthen-our-national-and-economic-security/
- Selected window: `3_day` ending on `2025-04-04`
- Daily sum RMSD: `0.002575099961`
- Top RMSD chain: `JPY -> SGD -> CHF -> JPY`
- Top event-alignment chain: `EUR -> USD -> SGD -> EUR`
- Top alignment chain RMSD rank: `10`
- Alignment score: `1.250621414400`

### Dominant Categories

- `trade_policy` score=100, impact=80, direction=50
- `geopolitics` score=90, impact=60, direction=30
- `supply_chain` score=80, impact=50, direction=20
- `defense_security` score=80, impact=50, direction=30
- `macro_growth` score=80, impact=40, direction=20

### Dominant Currencies

- `USD` score=100, impact=80, direction=50
- `EUR` score=80, impact=50, direction=-20
- `CNH` score=80, impact=50, direction=-20
- `CAD` score=60, impact=30, direction=0
- `JPY` score=40, impact=20, direction=0

### Interpretation

The official event is represented by ANAS as a trade_policy, geopolitics, macro_growth, supply_chain exposure with currency pressure around USD, EUR, CNH, CAD. In the 3_day window, FrictionGraph's largest standalone RMSD chain is JPY -> SGD -> CHF -> JPY, while the strongest event-overlap chain is EUR -> USD -> SGD -> EUR. These are different chains, which helps separate broad market stress from event-specific currency-chain alignment.

Caution: This case links official-event exposure to nearby FrictionGraph chain behavior. It is an explanatory alignment record, not a causal claim or trading signal.

### Tableau Inputs

- `output/alignment/event_alignment_summary.csv`
- `output/alignment/event_chain_alignment.csv`
- `output/alignment/waterfall_category_daily.csv`
- `output/alignment/waterfall_currency_daily.csv`
