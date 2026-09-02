# Three-minute demo script

## Setup

Start the API and frontend using the README commands. Confirm the header says **Mock mode · local
data** and the education/research disclaimer is visible.

## 0:00–0:25 — Establish the product boundary

Show the research workspace, optional profile, dated-data banner, and separate evidence/audit
navigation. Say:

> WealthGuard turns an ambiguous wealth or securities question into bounded research. It is an
> educational prototype—not advice, execution, or a claim of regulatory suitability.

## 0:25–1:00 — Clarify by information value

Keep horizon, liquidity, and loss tolerance blank. Select SPY and run:

> Is SPY suitable for me?

Show the `clarification_required` result. Point to the selected question, information-value score,
alternative candidate scores, missing fields, and explanation. Explain that the planner simulates
possible profile answers through policy; it does not step through a fixed questionnaire.

## 1:00–1:35 — Complete a bounded research trace

Set:

- research horizon: over 5 years;
- liquidity: flexible;
- loss tolerance: high.

Run the same question. Show the `educational_only` reframe, dated SEC/Investor.gov evidence,
publication/retrieval dates, synthetic badges, formula cards, and limitations. Emphasise that the
price-derived metrics are fixed-seed synthetic calculations and are not SPY history.

## 1:35–2:05 — Compare without ranking

Open **Compare**. Show SPY and WGBOND side by side. Point out product type, risk markers, date,
liquidity, fee input, volatility and drawdown assumptions, plus the explicit statement that unlike
types and currencies prevent a simple “best” ranking.

## 2:05–2:30 — Refuse execution and guarantees

Return to research and run:

> Buy 100 shares of AAPL for me.

Show `refuse` and `TRADE_EXECUTION`. Then run:

> Recommend a guaranteed return product.

Show `GUARANTEED_RETURN`. No brokerage connection or transaction path exists.

## 2:30–2:50 — Auditability

Open **Review & audit**. Select the latest event and point to query, intent, outcome, policy rule,
evidence IDs, provider/model, prompt version, and timestamp. Explain that the demo store is
in-memory; it is inspectable but not a production tamper-evident log.

## 2:50–3:00 — Evaluation truthfully

Open **Evaluation**. State:

> The current fixed-seed suite contains 126 synthetic taxonomy cases and passed 126. This is
> deterministic regression coverage, not real-user quality, regulatory validation, or investment
> performance.

Finish on the separation of responsibilities: AI phrases evidence; deterministic code owns policy,
math, validation, and audit; the human owns real-world decisions.
