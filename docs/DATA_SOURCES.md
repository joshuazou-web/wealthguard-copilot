# Data sources and provenance

## Offline design

The repository defaults to a small offline source pack. Public material is represented as short,
manually curated paraphrases rather than copied reports. Each note retains the source URL,
document type, publication date, local retrieval date, instrument link where relevant, provenance
status, and a SHA-256 checksum of the committed text.

## Public-source notes

| ID | Category | Source | Published | Retrieved | Use |
| --- | --- | --- | --- | --- | --- |
| `SEC-SPY-497-2026` | ETF prospectus | [SEC EDGAR](https://www.sec.gov/Archives/edgar/data/884394/000119312526022775/d77353d497.htm) | 2026-01-26 | 2026-09-02 | Structure, risks, dated ordinary operating expense |
| `SEC-AAPL-10K-2025` | Annual report | [SEC EDGAR](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm) | 2025-10-31 | 2026-09-02 | Dated revenue facts and disclosed risk categories |
| `INVESTOR-GOV-FEES-2025` | Investor education | [Investor.gov](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/mutual-fund-and-etf-fees-and-expenses-investor-bulletin) | 2025-07-23 | 2026-09-02 | Fee-comparison limitations |
| `INVESTOR-GOV-DIVERSIFY` | Investor education | [Investor.gov](https://www.investor.gov/introduction-investing/investing-basics/save-and-invest/diversify-your-investments) | 2025-01-01* | 2026-09-02 | Diversification education |

`*` The offline fixture uses a conservative page-date placeholder when a precise publication date
is not represented in the source note. It must not be interpreted as an independently verified
original publication date.

## Synthetic fixtures

`WG-BOND-FACTSHEET-2026` and `WG-CASH-DISCLOSURE-2026` are fictional product documents under the
`example.invalid` domain. WGBOND and WGCASH are fictional instruments. All sector/region weights,
liquidity assumptions, risk levels, minimum horizons, synthetic price paths, portfolios, and
scenarios are demonstration inputs.

The SPY and AAPL calculation series are also synthetic. Their names and selected dated document
facts are real; their generated returns, volatility, drawdown, exposure assumptions, and risk
labels are not historical analytics.

## Data freshness

The retrieval layer computes freshness from publication date. A stale label is a product warning,
not evidence that the underlying fact is false. The correct response is to expose the date and ask
the user to verify a current primary source where recency matters.

## Optional download adapters

No online downloader is required or enabled in the current version. A future adapter should:

1. use only sources whose terms and technical access permit the request;
2. store the original URL, headers/date, retrieval timestamp, checksum, and licence/usage note;
3. version rather than silently overwrite documents;
4. preserve raw text separately from summaries;
5. fail closed when provenance cannot be established.

No paid research report, scraped restricted source, user portfolio, brokerage data, or institution
internal data is included.

