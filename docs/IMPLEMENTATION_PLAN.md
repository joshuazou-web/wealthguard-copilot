# Implementation plan

## Product objective

WealthGuard Proofline（中文名：WealthGuard 证据防线）is a local-first
evidence-validation and quality-operations complement for existing securities assistants. It asks
the highest-value clarification question, grounds claims in dated evidence, delegates arithmetic
to deterministic tools, and places policy, bad-case governance and audit outside the language
model. It does not rebuild the host product's market data, news, community or trading journey.

It is educational software, not investment advice, execution, suitability certification,
or a regulated financial service.

## Existing project assessment

The source project, Converge, is a deterministic conversational search agent built around an
inverse user model, forward simulation of possible answers, expected-information-gain question
selection, confidence-gated output, intent override handling, traceable orchestration, and
ablation/robustness evaluation. The shopping catalog, hackathon evaluator, popularity prior,
slate optimization, and template-specific parsing are not transferable to finance.

## Capabilities retained as design ideas

- Explicit user/task state rather than treating each turn as an isolated query.
- Forward simulation of possible answers to estimate a clarification question's value.
- Confidence gates that ask, answer, caution, abstain, or refuse instead of always completing.
- Intent override that replaces stale state without silently retaining conflicting assumptions.
- An auditable trace for every question, policy decision, evidence item, and tool result.
- Deterministic test fixtures, ablations, and failure-focused evaluation.

## Financial capabilities added

- A non-regulatory research profile covering horizon, liquidity, loss tolerance, experience,
  product knowledge, concentration, and currency exposure.
- A deterministic policy engine for advice/execution boundaries and product-profile conflicts.
- Checksum-verified official PDF/HTML ingestion with page/paragraph retrieval and locators.
- Deterministic return, volatility, drawdown, fee, concentration, exposure, scenario, ratio,
  and comparison calculations.
- A model-provider boundary with a fully functional mock mode.
- A review surface for product-risk and compliance-oriented inspection.

## Non-goals

- No brokerage connection, order placement, personalised buy/sell/hold instruction, price
  prediction, guaranteed return, regulatory suitability certification, or production claim.
- No claim that synthetic portfolios, generated prices, or evaluation sessions represent real
  users, real performance, assets under management, conversion, revenue, or financial loss avoided.

## Users

1. Beginner investor learning concepts and document language.
2. Self-directed research user comparing dated public information.
3. Product risk or compliance reviewer inspecting boundaries and traces.

## Architecture

```text
React workspace
    -> FastAPI application
        -> intent + task-state manager
        -> clarification planner (outcome sensitivity + information gain)
        -> deterministic policy/suitability engine
        -> offline document retrieval + citation validator
        -> deterministic calculation tools
        -> mock/optional LLM response composer
        -> confidence/abstention gate
        -> append-only audit store
        -> deterministic evaluation runner
```

The backend is authoritative for policy, arithmetic, citations, and audit data. The frontend
renders structured results and never calculates financial metrics itself.

## Data design

- `UserProfile`: voluntarily supplied research context; no identity fields.
- `Instrument`: synthetic product metadata and risk characteristics.
- `OfficialSourceDocument`: URL, version, retrieval timestamp, media type, size and file SHA-256.
- `DocumentChunk`: extracted text with parent hash and page or paragraph/source-line location.
- `PricePoint`: deterministic synthetic price series used only for calculation demonstrations.
- `PortfolioHolding`: synthetic position and exposure data.
- `AuditEvent`: request, selected clarification, policy outcome, evidence and tool trace.

## Delivery phases

1. Independent repository, migration record, domain models and fixtures.
2. Policy, clarification, retrieval, calculation and audit modules.
3. FastAPI orchestration and mock-model mode.
4. Research, compare, portfolio, evidence, audit and evaluation UI.
5. 100+ deterministic cases, unit/integration tests, evaluation report and demo script.
6. Clean-environment run, visual QA, source-repository integrity check and truth audit.
7. P0 official pack, chunk citations, conflict/version gates and 39-case trace evaluation.

## Definition of done

- Starts locally without an API key and demonstrates the full journey.
- Every displayed metric comes from deterministic backend calculation.
- Every research claim has a source identifier and date, or is labelled as synthetic.
- Policy and suitability outcomes remain correct if the model layer is unavailable.
- Evaluation output is generated from committed cases and reproducible commands.
- The Converge working tree remains unchanged from the recorded baseline.
