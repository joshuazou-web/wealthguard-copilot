# Data sources and provenance

## Verified offline source pack

The default research path uses 13 original public files downloaded from allowlisted official
domains. `data/official/manifest.json` records URL, version, retrieval timestamp, media type, byte
size and SHA-256. Startup and corpus loading fail closed if a raw file or processed chunk changes.
The reproducible downloader never silently blesses a changed cached file; an intentional
replacement requires `--force` and a subsequent corpus/evaluation rebuild.

| Authority | ID | Type | Published/version date | Format |
| --- | --- | --- | --- | --- |
| SEC | `SEC-SPY-497-2026` | ETF prospectus | 2026-01-26 | HTML |
| SEC | `SEC-SPY-497-2025` | ETF prospectus | 2025-01-28 | HTML |
| SEC | `SEC-AAPL-10K-2025` | Annual report | 2025-10-31 | HTML |
| SEC | `SEC-AAPL-10K-2024` | Annual report | 2024-11-01 | HTML |
| HKEX | `HKEX-ANNUAL-REPORT-2025` | Annual report | 2026-03-16 | PDF |
| HKEX | `HKEX-ETF-HANDBOOK` | Investor education | Not stated in source | PDF |
| HKEX | `HKEX-ETP-EDUCATION-2026` | Investor education | Page updated 2026-04-28 | HTML |
| SZSE | `SZSE-ENERGY-ETF-PROSPECTUS-2023` | ETF prospectus | 2023-08-17 | PDF |
| SZSE | `SZSE-ETF-LOF-EDUCATION-2023` | Investor education | 2023-03-17 | HTML |
| SZSE | `SZSE-ETF-LISTING-NOTICE-2026` | Exchange notice | 2026-01-20 | HTML |
| CSRC | `CSRC-FUND-SALES-FEE-RULE-2025` | Regulatory rule | 2025-12-31 | HTML |
| CSRC | `CSRC-INVESTOR-PROTECTION-FUND-RULE-2016` | Investor protection rule | 2016 revision | PDF |
| CSRC | `CSRC-SECURITIES-INVESTMENT-FUND-LAW-2012` | Regulatory rule | 2012 revision | HTML |

Complete official URLs are in `data/official/source_catalog.json`; the UI also links each register
entry to its official origin. The repository does not imply endorsement by any authority or issuer.

## Extraction and location

- PDF text is extracted per page; chunks never cross a page boundary and retain a one-based page.
- HTML blocks retain global paragraph numbers, nearest heading where available, and source lines.
- Every chunk has its own SHA-256 plus its parent file hash. A citation resolves to the file, exact
  span, location, source date, retrieval time and verbatim extracted text.
- The internal viewer escapes source text. Cached originals are served inline only for PDFs;
  HTML opens on the official domain rather than executing a cached page.

The deterministic build produced 1,714 chunks. Rebuild with
`python scripts/build_official_corpus.py` after an intentional source/extractor change.

## Versions, freshness and conflicts

Documents sharing an instrument and type are labelled `latest` or `older_version`; an explicitly
undated source is `undated`. Publication age independently produces `current_for_demo`,
`review_date`, `stale` or `future_dated`. A stale label is a warning, not a claim that a fact is false.

Structured numbers are compared only under the same instrument and fact key, which should include
the reporting period. Two differing source values produce `SOURCE_CONFLICT`, a `caution` outcome
and required date/version review. The product does not silently choose one value.

## Synthetic fixtures remain separate

WGBOND and WGCASH, their documents, price paths, portfolios, exposures and scenarios remain
`synthetic_demo_data`. SPY and AAPL return/volatility/drawdown series are also synthetic calculation
fixtures, never real historical performance. No paid report, restricted scrape, real portfolio,
brokerage data or institution-internal data is included.
