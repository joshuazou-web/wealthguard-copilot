"""Offline, dated research notes and deterministic synthetic calculation fixtures."""

from __future__ import annotations

import hashlib
import math
import random
from datetime import date

from .models import DataStatus, Instrument, ResearchDocument

INSTRUMENTS = [
    Instrument(
        instrument_id="SPY",
        symbol="SPY",
        name="State Street SPDR S&P 500 ETF Trust",
        instrument_type="ETF",
        issuer="State Street",
        currency="USD",
        region="United States",
        risk_level=4,
        complexity="standard",
        min_horizon_months=60,
        liquidity_days=1,
        expense_ratio=0.000945,
        sectors={"Technology": 0.32, "Financials": 0.13, "Health Care": 0.12, "Other": 0.43},
        regions={"United States": 1.0},
        as_of=date(2026, 1, 26),
    ),
    Instrument(
        instrument_id="AAPL",
        symbol="AAPL",
        name="Apple Inc. common stock",
        instrument_type="Equity",
        issuer="Apple Inc.",
        currency="USD",
        region="United States",
        risk_level=5,
        complexity="standard",
        min_horizon_months=60,
        liquidity_days=1,
        expense_ratio=0.0,
        sectors={"Technology": 1.0},
        regions={"Global operations": 1.0},
        as_of=date(2025, 9, 27),
    ),
    Instrument(
        instrument_id="WGBOND",
        symbol="WGBOND",
        name="WealthGuard Asia Income Bond Fund (synthetic)",
        instrument_type="Bond fund",
        issuer="WealthGuard Synthetic Research Lab",
        currency="SGD",
        region="Asia Pacific",
        risk_level=2,
        complexity="standard",
        min_horizon_months=24,
        liquidity_days=3,
        expense_ratio=0.0065,
        sectors={"Sovereign": 0.45, "Financials": 0.25, "Industrial": 0.20, "Other": 0.10},
        regions={"Singapore": 0.35, "Japan": 0.25, "Australia": 0.20, "Other APAC": 0.20},
        as_of=date(2026, 6, 30),
    ),
    Instrument(
        instrument_id="WGCASH",
        symbol="WGCASH",
        name="WealthGuard Liquidity Reserve (synthetic)",
        instrument_type="Money market fund",
        issuer="WealthGuard Synthetic Research Lab",
        currency="SGD",
        region="Singapore",
        risk_level=1,
        complexity="standard",
        min_horizon_months=1,
        liquidity_days=1,
        expense_ratio=0.0025,
        sectors={"Cash equivalents": 0.55, "Sovereign": 0.30, "Bank deposits": 0.15},
        regions={"Singapore": 1.0},
        as_of=date(2026, 6, 30),
    ),
]


_DOCUMENT_SPECS = [
    {
        "document_id": "SEC-SPY-497-2026",
        "instrument_id": "SPY",
        "title": "SPY prospectus research note",
        "document_type": "ETF prospectus",
        "source_name": "U.S. Securities and Exchange Commission EDGAR",
        "source_url": "https://www.sec.gov/Archives/edgar/data/884394/000119312526022775/d77353d497.htm",
        "published_at": date(2026, 1, 26),
        "retrieved_at": date(2026, 9, 2),
        "content": (
            "Curated paraphrase for the offline demo: the trust is listed as SPY and is designed "
            "to hold a portfolio corresponding to the S&P 500. Its prospectus describes loss of "
            "principal and market-price divergence as investment risks. Estimated ordinary "
            "operating expenses were stated as 0.0945% of average net assets on the document date."
        ),
        "key_facts": [
            "The product is an exchange-traded unit investment trust linked to the S&P 500.",
            "The prospectus identifies investment loss and market-price divergence risks.",
            "The dated prospectus states estimated ordinary operating expenses of 0.0945%.",
        ],
        "structured_facts": {"expense_ratio": "0.000945", "benchmark": "S&P 500"},
        "data_status": DataStatus.PUBLIC_PARAPHRASE,
    },
    {
        "document_id": "SEC-AAPL-10K-2025",
        "instrument_id": "AAPL",
        "title": "Apple 2025 Form 10-K research note",
        "document_type": "Annual report",
        "source_name": "U.S. Securities and Exchange Commission EDGAR",
        "source_url": "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927.htm",
        "published_at": date(2025, 10, 31),
        "retrieved_at": date(2026, 9, 2),
        "content": (
            "Curated paraphrase for the offline demo: Apple reported fiscal-2025 total net sales "
            "of USD 416.161 billion, including USD 109.158 billion from Services. The filing also "
            "describes global competition, supply-chain concentration, foreign-exchange exposure, "
            "regulatory change and dependence on successful product introduction as risk factors."
        ),
        "key_facts": [
            "Fiscal-2025 total net sales were reported as USD 416.161 billion.",
            "Fiscal-2025 Services net sales were reported as USD 109.158 billion.",
            "The filing discusses competition, supply chain, currency and regulatory risks.",
        ],
        "structured_facts": {
            "fiscal_2025_total_net_sales_usd_millions": "416161",
            "fiscal_2025_services_net_sales_usd_millions": "109158",
        },
        "data_status": DataStatus.PUBLIC_PARAPHRASE,
    },
    {
        "document_id": "INVESTOR-GOV-FEES-2025",
        "instrument_id": None,
        "title": "Mutual fund and ETF fees research note",
        "document_type": "Official investor education",
        "source_name": "Investor.gov",
        "source_url": "https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/mutual-fund-and-etf-fees-and-expenses-investor-bulletin",
        "published_at": date(2025, 7, 23),
        "retrieved_at": date(2026, 9, 2),
        "content": (
            "Curated paraphrase for the offline demo: investors should review prospectus fee tables "
            "and compare both direct and indirect costs. Expense ratios do not necessarily capture "
            "every cost, and layered fund structures may expose investors to multiple fee levels."
        ),
        "key_facts": [
            "Prospectus fee tables should be reviewed before comparing funds or ETFs.",
            "Expense ratios may not include every direct or indirect investment cost.",
            "Layered fund structures can expose an investor to more than one level of fees.",
        ],
        "structured_facts": {},
        "data_status": DataStatus.PUBLIC_PARAPHRASE,
    },
    {
        "document_id": "INVESTOR-GOV-DIVERSIFY",
        "instrument_id": None,
        "title": "Diversification research note",
        "document_type": "Official investor education",
        "source_name": "Investor.gov",
        "source_url": "https://www.investor.gov/introduction-investing/investing-basics/save-and-invest/diversify-your-investments",
        "published_at": date(2025, 1, 1),
        "retrieved_at": date(2026, 9, 2),
        "content": (
            "Curated paraphrase for the offline demo: diversification spreads exposure across "
            "investments. It may reduce the effect of a single loss but cannot prevent losses when "
            "markets decline broadly and does not guarantee a positive result."
        ),
        "key_facts": [
            "Diversification spreads exposure rather than guaranteeing against loss.",
            "Broad market declines can still produce losses in a diversified portfolio.",
        ],
        "structured_facts": {},
        "data_status": DataStatus.PUBLIC_PARAPHRASE,
    },
    {
        "document_id": "WG-BOND-FACTSHEET-2026",
        "instrument_id": "WGBOND",
        "title": "Synthetic Asia income bond fund factsheet",
        "document_type": "Fund factsheet",
        "source_name": "WealthGuard Synthetic Research Lab",
        "source_url": "https://example.invalid/wealthguard/wgbond/factsheet-2026-06",
        "published_at": date(2026, 6, 30),
        "retrieved_at": date(2026, 9, 2),
        "content": (
            "Synthetic demo fixture: the fund holds a diversified set of Asia-Pacific sovereign "
            "and investment-grade corporate bonds. It carries interest-rate, credit, currency and "
            "liquidity risk and assumes a three-business-day redemption window."
        ),
        "key_facts": [
            "Synthetic allocation includes sovereign and investment-grade corporate bonds.",
            "Synthetic risk factors include rates, credit, currency and liquidity.",
            "Synthetic redemption assumption is three business days.",
        ],
        "structured_facts": {"liquidity_days": "3"},
        "data_status": DataStatus.SYNTHETIC,
    },
    {
        "document_id": "WG-CASH-DISCLOSURE-2026",
        "instrument_id": "WGCASH",
        "title": "Synthetic liquidity reserve risk disclosure",
        "document_type": "Product risk disclosure",
        "source_name": "WealthGuard Synthetic Research Lab",
        "source_url": "https://example.invalid/wealthguard/wgcash/risk-2026-06",
        "published_at": date(2026, 6, 30),
        "retrieved_at": date(2026, 9, 2),
        "content": (
            "Synthetic demo fixture: the reserve invests in cash equivalents, short sovereign "
            "instruments and deposits. It is modelled as low volatility but is not represented as "
            "a bank deposit, guaranteed product or loss-free investment."
        ),
        "key_facts": [
            "Synthetic holdings are cash equivalents, sovereign instruments and deposits.",
            "The synthetic product is not represented as guaranteed or loss-free.",
        ],
        "structured_facts": {"guaranteed": "false", "liquidity_days": "1"},
        "data_status": DataStatus.SYNTHETIC,
    },
]


def documents() -> list[ResearchDocument]:
    result: list[ResearchDocument] = []
    for spec in _DOCUMENT_SPECS:
        checksum = hashlib.sha256(spec["content"].encode("utf-8")).hexdigest()
        result.append(ResearchDocument(**spec, checksum=checksum))
    return result


def synthetic_prices(instrument_id: str, months: int = 36, seed: int = 7319) -> list[float]:
    """Return a deterministic illustrative monthly series; never actual market performance."""
    profiles = {
        "SPY": (0.0065, 0.043, 100.0),
        "AAPL": (0.0080, 0.070, 100.0),
        "WGBOND": (0.0030, 0.016, 100.0),
        "WGCASH": (0.0018, 0.002, 100.0),
    }
    mean, volatility, start = profiles[instrument_id]
    rng = random.Random(f"{seed}:{instrument_id}")
    prices = [start]
    for month in range(months):
        cyclical = math.sin((month + 1) / 4.0) * volatility * 0.22
        shock = rng.gauss(mean + cyclical, volatility)
        prices.append(round(max(1.0, prices[-1] * (1.0 + shock)), 6))
    return prices


def instrument_map() -> dict[str, Instrument]:
    return {instrument.instrument_id: instrument for instrument in INSTRUMENTS}
