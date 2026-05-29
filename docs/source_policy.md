# ANAS Source Policy Registry

This registry defines which sources ANAS may use for the public demo and future
training corpus. The project is designed to be safe to share with employers, so
source governance is part of the core system rather than an afterthought.

## Policy Levels

```text
green   Use for raw storage, labeling, private training, and public derived demos.
yellow  Use only with restrictions. Store metadata/links and derived signals, not bulk raw text.
red     Do not use for training corpus or public demo data.
```

## Default Rules

- Prefer official sources, official APIs, RSS feeds, downloadable documents, or
  government publication systems.
- Do not use copyrighted news article full text as training data.
- Do not publish raw official documents in this repository unless their terms
  clearly allow redistribution.
- Public examples should use synthetic records, tiny excerpts where allowed, or
  derived vectors/aggregates.
- Private/local storage may contain raw official documents only when the source
  policy permits storage.
- Every ingested document must keep provenance:
  `source`, `source_url`, `published_at`, `fetched_at`, `content_sha256`,
  `license_status`, and `source_policy_id`.

## Green Sources

### Federal Reserve Board

```json
{
  "source_policy_id": "fed_board_public_domain",
  "source": "Federal Reserve Board",
  "status": "green",
  "license_status": "public_domain_unless_noted",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "FOMC statements",
    "FOMC minutes",
    "speeches",
    "testimony",
    "press releases"
  ],
  "notes": "Use text from official Federal Reserve pages. Avoid logos, images, and third-party materials."
}
```

Rationale: Federal Reserve Board website information is generally public domain
unless otherwise noted.

### Bureau of Labor Statistics

```json
{
  "source_policy_id": "bls_public_domain",
  "source": "Bureau of Labor Statistics",
  "status": "green",
  "license_status": "public_domain",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "CPI releases",
    "PPI releases",
    "Employment Situation releases",
    "wage and labor market releases",
    "public data API records"
  ],
  "notes": "Credit BLS as the source when presenting derived outputs."
}
```

### Bureau of Economic Analysis

```json
{
  "source_policy_id": "bea_public_domain",
  "source": "Bureau of Economic Analysis",
  "status": "green",
  "license_status": "public_domain_unless_noted",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "GDP releases",
    "PCE releases",
    "personal income releases",
    "corporate profits releases",
    "BEA API records"
  ],
  "notes": "Use official BEA text and data. Avoid third-party embedded content if present."
}
```

### U.S. Energy Information Administration

```json
{
  "source_policy_id": "eia_public_domain",
  "source": "U.S. Energy Information Administration",
  "status": "green",
  "license_status": "public_domain_government_information",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "Weekly Petroleum Status Report",
    "natural gas storage reports",
    "short-term energy outlook summaries",
    "EIA API records"
  ],
  "notes": "Useful for oil, gas, energy security, CAD/USD exposure, and commodity shock cases in the current FrictionGraph universe."
}
```

### Federal Register

```json
{
  "source_policy_id": "federal_register_public_domain",
  "source": "Federal Register",
  "status": "green",
  "license_status": "public_domain_government_publication",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "official rules",
    "proposed rules",
    "notices",
    "trade restrictions",
    "export control rule changes"
  ],
  "notes": "Strong source for official policy events with clear dates and agencies."
}
```

## Green / Yellow Sources

These are official sources, but each connector should verify page-level terms and
avoid third-party materials.

### U.S. Trade Representative

```json
{
  "source_policy_id": "ustr_official_releases",
  "source": "Office of the U.S. Trade Representative",
  "status": "green_yellow",
  "license_status": "official_us_government_source_check_page_terms",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "tariff announcements",
    "Section 301 updates",
    "trade investigation notices",
    "official press releases"
  ],
  "notes": "Primary source for trade_policy and US-China exposure. Confirm page provenance and avoid non-government embedded material."
}
```

### U.S. Treasury / OFAC

```json
{
  "source_policy_id": "treasury_ofac_official",
  "source": "U.S. Treasury / OFAC",
  "status": "green_yellow",
  "license_status": "official_us_government_source_check_page_terms",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "sanctions updates",
    "OFAC notices",
    "Treasury press releases",
    "FiscalData API records"
  ],
  "notes": "Useful for sanctions, geopolitics, USD liquidity, safe-haven, and country-risk events."
}
```

### U.S. Department of Commerce / BIS

```json
{
  "source_policy_id": "commerce_bis_official",
  "source": "U.S. Department of Commerce / BIS",
  "status": "green_yellow",
  "license_status": "official_us_government_source_check_page_terms",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "export control announcements",
    "entity list updates",
    "semiconductor restrictions",
    "AI/chip-related controls"
  ],
  "notes": "Core source for semiconductors, artificial_intelligence, supply_chain, and trade_policy cases."
}
```

### White House

```json
{
  "source_policy_id": "white_house_official",
  "source": "White House",
  "status": "green_yellow",
  "license_status": "official_us_government_source_check_page_terms",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true,
  "preferred_content": [
    "executive orders",
    "fact sheets",
    "official statements",
    "trade and security policy announcements"
  ],
  "notes": "Use only official text. Avoid campaign material, photos, videos, and third-party content."
}
```

## Yellow Sources

### SEC EDGAR

```json
{
  "source_policy_id": "sec_edgar_limited",
  "source": "SEC EDGAR",
  "status": "yellow",
  "license_status": "public_access_but_issuer_text_rights_may_vary",
  "raw_storage_allowed": false,
  "ml_training_allowed": false,
  "public_demo_allowed": false,
  "preferred_content": [
    "metadata",
    "filing date",
    "issuer identifiers",
    "structured XBRL facts"
  ],
  "notes": "Use cautiously. For ANAS v1, do not use company narrative text as model-training raw corpus."
}
```

### International Official Sources

```json
{
  "source_policy_id": "international_official_review_required",
  "source": "ECB / BoJ / BoE / EU Commission / WTO / IMF / World Bank",
  "status": "yellow",
  "license_status": "source_specific_review_required",
  "raw_storage_allowed": false,
  "ml_training_allowed": false,
  "public_demo_allowed": true,
  "preferred_content": [
    "metadata",
    "links",
    "derived event vectors after policy review"
  ],
  "notes": "Do not bulk-ingest raw text until each source's terms are reviewed and documented."
}
```

## Red Sources

```json
{
  "source_policy_id": "copyrighted_news_full_text",
  "source": "copyrighted news publishers",
  "status": "red",
  "license_status": "copyrighted",
  "raw_storage_allowed": false,
  "ml_training_allowed": false,
  "public_demo_allowed": false,
  "examples": [
    "Guardian article full text",
    "Reuters article full text",
    "Bloomberg article full text",
    "WSJ article full text",
    "FT article full text",
    "CNBC article full text"
  ],
  "notes": "May be referenced by URL for human-readable case context, but do not store full text or use as training corpus."
}
```

## First 10-Event Seed Set Criteria

The first demo set should be selected from green or green/yellow sources and
should cover the categories most likely to align with FrictionGraph currency
chains:

- trade_policy
- geopolitics
- sanctions
- energy_oil_gas
- semiconductors
- artificial_intelligence
- monetary_policy
- inflation

Each event should have:

```json
{
  "event_id": "stable_unique_id",
  "event_date": "YYYY-MM-DD",
  "source_policy_id": "policy_id_from_this_registry",
  "source": "official source",
  "document_type": "official_event_type",
  "title": "official title",
  "source_url": "official URL",
  "raw_storage_allowed": true,
  "ml_training_allowed": true,
  "public_demo_allowed": true
}
```

## Public Demo Rule

For the public portfolio:

- show the source URL and metadata
- show the generated exposure vectors
- show FrictionGraph derived response metrics
- show waterfall visualizations and interpretation
- do not publish bulk raw documents
- do not publish raw tick data
- do not publish API keys or private S3 paths
