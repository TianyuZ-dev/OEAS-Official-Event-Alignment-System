# ANAS 10-Event Seed Set

This document defines the first 10 official events for the ANAS demo.

The seed set is intentionally small. Its purpose is to validate the workflow:

```text
official source metadata
  -> ANAS exposure extraction
  -> daily category/currency aggregation
  -> FrictionGraph chain alignment
  -> waterfall-ready demo output
```

It is not intended to prove statistical predictability.

## Selection Rules

Seed events should:

- fall inside the current FrictionGraph processed date range
  (`2024-01-02` to `2026-01-01`)
- come from green or green/yellow sources in `docs/source_policy.md`
- have official URLs
- cover geopolitical, trade, sanctions, energy, chips/AI, monetary policy, and inflation themes
- map naturally to the current FrictionGraph chain currencies:
  `CAD, CHF, EUR, JPY, SGD, USD`
- optionally include proxy instruments:
  `CNH, XAU`

## Current FrictionGraph Alignment Space

```text
6 chain currencies:
CAD, CHF, EUR, JPY, SGD, USD

32 triangle chains built from those 6 currencies

configured proxy instruments:
CNH, XAU
```

## Seed Events

### 1. Russia Oil / Shipping Sanctions

```json
{
  "event_id": "treasury_2024_02_23_sovcomflot_sanctions",
  "event_date": "2024-02-23",
  "source_policy_id": "treasury_ofac_official",
  "source": "U.S. Treasury / OFAC",
  "document_type": "sanctions_press_release",
  "title": "U.S. Treasury Designates Russian State-Owned Sovcomflot, Russia's Largest Shipping Company",
  "source_url": "https://home.treasury.gov/news/press-releases/jy2121",
  "primary_categories": ["sanctions", "geopolitics", "energy_oil_gas", "supply_chain"],
  "country_focus": ["US", "RU"],
  "currency_focus": ["USD", "CAD", "CHF", "JPY", "XAU"],
  "alignment_note": "Russia oil/shipping sanctions may align with USD funding pressure, oil-linked CAD exposure, and safe-haven CHF/JPY/XAU behavior."
}
```

### 2. March 2024 CPI Release

```json
{
  "event_id": "bls_2024_04_10_cpi_march_2024",
  "event_date": "2024-04-10",
  "source_policy_id": "bls_public_domain",
  "source": "Bureau of Labor Statistics",
  "document_type": "cpi_release",
  "title": "Consumer Price Index - March 2024",
  "source_url": "https://www.bls.gov/news.release/archives/cpi_04102024.htm",
  "primary_categories": ["inflation", "monetary_policy", "macro_growth", "equities_risk", "energy_oil_gas"],
  "country_focus": ["US"],
  "currency_focus": ["USD", "CAD", "CHF", "JPY"],
  "alignment_note": "Hotter inflation and gasoline/shelter components can affect USD rates expectations, CAD energy sensitivity, and safe-haven chains."
}
```

### 3. Iran UAV / Steel Sanctions After Israel Attack

```json
{
  "event_id": "treasury_2024_04_18_iran_uav_steel_sanctions",
  "event_date": "2024-04-18",
  "source_policy_id": "treasury_ofac_official",
  "source": "U.S. Treasury / OFAC",
  "document_type": "sanctions_press_release",
  "title": "Treasury Targets Iranian UAV Program, Steel Industry, and Automobile Companies in Response to Unprecedented Attack on Israel",
  "source_url": "https://home.treasury.gov/news/press-releases/jy2270",
  "primary_categories": ["geopolitics", "sanctions", "defense_security", "commodities_metals", "energy_oil_gas"],
  "country_focus": ["US", "IR", "IL"],
  "currency_focus": ["USD", "CHF", "JPY", "EUR", "XAU"],
  "alignment_note": "Middle East escalation and sanctions can map to safe-haven CHF/JPY/XAU pressure and broader USD/EUR risk channels."
}
```

### 4. June 2024 FOMC Statement

```json
{
  "event_id": "fed_2024_06_12_fomc_statement",
  "event_date": "2024-06-12",
  "source_policy_id": "fed_board_public_domain",
  "source": "Federal Reserve Board",
  "document_type": "fomc_statement",
  "title": "Federal Reserve issues FOMC statement",
  "source_url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20240612a.htm",
  "primary_categories": ["monetary_policy", "inflation", "macro_growth", "equities_risk"],
  "country_focus": ["US"],
  "currency_focus": ["USD", "CAD", "EUR", "JPY", "CHF"],
  "alignment_note": "FOMC rate guidance is a direct USD policy anchor and can propagate through all USD-linked FrictionGraph chains."
}
```

### 5. China Section 301 Tariff Final Modifications

```json
{
  "event_id": "ustr_2024_09_13_china_section_301_tariffs",
  "event_date": "2024-09-13",
  "source_policy_id": "ustr_official_releases",
  "source": "Office of the U.S. Trade Representative",
  "document_type": "trade_policy_press_release",
  "title": "USTR Finalizes Action on China Tariffs Following Statutory Four-Year Review",
  "source_url": "https://ustr.gov/about-us/policy-offices/press-office/press-releases/2024/september/ustr-finalizes-action-china-tariffs-following-statutory-four-year-review",
  "primary_categories": ["trade_policy", "geopolitics", "supply_chain", "semiconductors", "commodities_metals"],
  "country_focus": ["US", "CN"],
  "currency_focus": ["USD", "CNH", "SGD", "JPY", "CHF"],
  "alignment_note": "US-China tariff action maps to USD/CNH proxy pressure and Asia trade-hub exposure through SGD, JPY, and safe-haven CHF."
}
```

### 6. September 2024 FOMC Rate Cut

```json
{
  "event_id": "fed_2024_09_18_fomc_rate_cut",
  "event_date": "2024-09-18",
  "source_policy_id": "fed_board_public_domain",
  "source": "Federal Reserve Board",
  "document_type": "fomc_statement",
  "title": "Federal Reserve issues FOMC statement",
  "source_url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary20240918a.htm",
  "primary_categories": ["monetary_policy", "inflation", "macro_growth", "equities_risk"],
  "country_focus": ["US"],
  "currency_focus": ["USD", "EUR", "JPY", "CHF", "CAD", "SGD"],
  "alignment_note": "The 50 bp rate cut is a high-salience USD monetary event and should be useful for testing broad chain response alignment."
}
```

### 7. Gazprombank / Russia Financial Sanctions

```json
{
  "event_id": "treasury_2024_11_21_gazprombank_sanctions",
  "event_date": "2024-11-21",
  "source_policy_id": "treasury_ofac_official",
  "source": "U.S. Treasury / OFAC",
  "document_type": "sanctions_press_release",
  "title": "Treasury Sanctions Gazprombank and Takes Additional Steps to Curtail Russia's Use of the International Financial System",
  "source_url": "https://home.treasury.gov/news/press-releases/jy2725",
  "primary_categories": ["sanctions", "geopolitics", "energy_oil_gas", "macro_growth"],
  "country_focus": ["US", "RU"],
  "currency_focus": ["USD", "EUR", "CHF", "JPY", "XAU"],
  "alignment_note": "A major Russian financial sanctions event can test USD/EUR funding stress and safe-haven chain behavior."
}
```

### 8. China Advanced Semiconductor Export Controls

```json
{
  "event_id": "bis_2024_12_02_china_semiconductor_controls",
  "event_date": "2024-12-02",
  "source_policy_id": "commerce_bis_official",
  "source": "U.S. Department of Commerce / BIS",
  "document_type": "export_control_press_release",
  "title": "Commerce Strengthens Export Controls to Restrict China's Capability to Produce Advanced Semiconductors for Military Applications",
  "source_url": "https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military",
  "primary_categories": ["semiconductors", "artificial_intelligence", "trade_policy", "geopolitics", "defense_security", "supply_chain"],
  "country_focus": ["US", "CN"],
  "currency_focus": ["USD", "CNH", "SGD", "JPY", "CHF"],
  "alignment_note": "This is the cleanest seed event for chip/AI controls and Asia technology/trade exposure."
}
```

### 9. Reciprocal Tariff National Emergency

```json
{
  "event_id": "whitehouse_2025_04_02_reciprocal_tariffs",
  "event_date": "2025-04-02",
  "source_policy_id": "white_house_official",
  "source": "White House",
  "document_type": "executive_order_fact_sheet",
  "title": "President Donald J. Trump Declares National Emergency to Increase our Competitive Edge, Protect our Sovereignty, and Strengthen our National and Economic Security",
  "source_url": "https://www.whitehouse.gov/fact-sheets/2025/04/fact-sheet-president-donald-j-trump-declares-national-emergency-to-increase-our-competitive-edge-protect-our-sovereignty-and-strengthen-our-national-and-economic-security/",
  "primary_categories": ["trade_policy", "geopolitics", "macro_growth", "inflation", "supply_chain", "equities_risk"],
  "country_focus": ["US", "CN", "EU", "CA", "JP", "SG"],
  "currency_focus": ["USD", "CNH", "EUR", "CAD", "JPY", "SGD", "CHF"],
  "alignment_note": "Broad tariff action is a strong candidate for the first waterfall case because it touches many countries and chain currencies."
}
```

### 10. April 2025 EIA STEO Oil / Trade Policy Update

```json
{
  "event_id": "eia_2025_04_10_steo_trade_oil_prices",
  "event_date": "2025-04-10",
  "source_policy_id": "eia_public_domain",
  "source": "U.S. Energy Information Administration",
  "document_type": "steo_press_release",
  "title": "EIA expects less oil demand and lower oil and gasoline prices in an uncertain market",
  "source_url": "https://www.eia.gov/pressroom/releases/press567.php",
  "primary_categories": ["energy_oil_gas", "macro_growth", "trade_policy", "commodities_metals", "inflation"],
  "country_focus": ["US", "CA", "CN"],
  "currency_focus": ["CAD", "USD", "JPY", "CHF", "XAU"],
  "alignment_note": "Energy demand and oil price revisions can test CAD/USD sensitivity and safe-haven response during trade-policy uncertainty."
}
```

## Coverage Check

Category coverage:

```text
monetary_policy: events 4, 6
inflation: events 2, 4, 6, 9, 10
geopolitics: events 1, 3, 5, 7, 8, 9
trade_policy: events 5, 8, 9, 10
sanctions: events 1, 3, 7
energy_oil_gas: events 1, 3, 7, 10
semiconductors: events 5, 8
artificial_intelligence: event 8
supply_chain: events 1, 5, 8, 9
defense_security: events 3, 8
equities_risk: events 2, 4, 6, 9
```

Currency/proxy coverage:

```text
USD: all events
CAD: events 1, 2, 4, 6, 9, 10
CHF: events 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
EUR: events 3, 4, 6, 7, 9
JPY: events 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
SGD: events 5, 6, 8, 9
CNH proxy: events 5, 8, 9
XAU proxy: events 1, 3, 7, 10
```

## Next Step

After review, convert these records into machine-readable seed data:

```text
data/seeds/official_events_seed_v1.json
```

Then the pipeline can fetch official text, compute `content_sha256`, and run the
expanded ANAS exposure extractor.
