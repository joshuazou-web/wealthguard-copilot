# Product case study

## Context

Wealth and securities questions frequently arrive as apparently simple requests—“Is this fund
suitable?”, “Which one is better?”, or “Should I buy this stock?”—but the safe and useful answer
depends on missing context, task boundaries, dated evidence, and correct calculations. A fluent
response can conceal each of those gaps.

WealthGuard Copilot is a portfolio project exploring a product response to that problem. It is a
local research prototype, not a live financial service, and all profiles, portfolios, evaluation
sessions, and market-series calculations are synthetic.

## Product thesis

The system should not maximise answer rate. It should maximise the share of responses that are
appropriately framed, supported by inspectable evidence, numerically reproducible, and honest
about uncertainty.

Three product principles follow:

1. **Clarify by decision value.** Ask one question that could change the research or policy path,
   not every question that could possibly be collected.
2. **Separate controls from language.** A model can explain evidence; it does not own transaction
   boundaries, key calculations, or the validity of its own citations.
3. **Make failure reviewable.** A reviewer should be able to reconstruct what the system believed,
   why it asked, what evidence and tools it used, and why it answered or declined.

## Users and jobs

### Beginner investor

Learn how product type, risk, fees, liquidity, and diversification affect a research question
without being pushed toward a transaction.

### Self-directed research user

Compare a small set of instruments, inspect dated public documents, and reproduce calculated
metrics and assumptions.

### Product risk or compliance reviewer

Inspect advice/execution boundaries, profile-product conflicts, refusal cases, citation lineage,
confidence, provider version, and regression failures.

## Journey and product decisions

1. The query is classified as education, research, comparison, portfolio analysis, personalised
   advice, or trade execution.
2. For tasks whose safe framing depends on context, the planner identifies missing fields.
3. Each possible answer is simulated through the deterministic policy engine. Outcome entropy,
   answer entropy, and task-specific relevance produce a transparent information-value score.
4. The highest-scoring question is shown with alternatives and a reason.
5. Policy rules independently check execution, guarantee, bypass, sensitive-data, distress,
   minor, horizon, liquidity, loss-tolerance, and complexity conflicts.
6. The retriever returns dated official-source chunks. Page/paragraph location, freshness,
   version status, provenance and parent checksum remain
   attached to each result.
7. Deterministic tools calculate research metrics from fixed synthetic fixtures.
8. The provider composes only from the supplied evidence; citation identifiers are validated.
9. The controller answers, cautions, reframes, asks, refuses, or routes to human review.
10. The audit store records the trace.

## Why the interface is not chat-only

The main question is only one input into a research task. The desktop workspace keeps the
voluntary profile, selected instruments, evidence dates, tool results, policy trace, limitations,
and confidence visible. Dedicated comparison, portfolio, evidence, audit, and evaluation views
support the two non-chat jobs: deliberate analysis and independent review.

## Scope choices

The first version uses an offline data pack and in-memory audit store. This makes the demo
reproducible, avoids paid dependencies, and prevents accidental presentation of live-looking
synthetic values. It intentionally does not include authentication, order execution, portfolio
optimisation, price forecasts, or jurisdiction-specific legal rules.

## Success definition

Success for this prototype is demonstrated by reproducible product controls—not user growth or
financial outcomes. The acceptance evidence is the running UI, unit and integration tests, 126
committed synthetic regression cases, generated evaluation artifacts, source register, and audit
trace. See `EVALUATION_REPORT.md` for the exact scope of those results.

## Next product experiments

- Double-annotate ambiguous queries and measure inter-rater agreement on intent and clarification.
- Replace fixed answer priors with calibrated priors learned from consented research sessions.
- Add source-span verification against downloaded official documents with versioned snapshots.
- Test whether “why this question” explanations improve voluntary profile completion and trust.
- Evaluate abstention and citation behaviour with unseen, adversarial, multilingual inputs.
- Add jurisdiction-specific policy packs only with qualified legal/compliance review.
