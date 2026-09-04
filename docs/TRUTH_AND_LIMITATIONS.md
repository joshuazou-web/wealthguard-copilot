# Truth and limitations register

## Claims supported by repository evidence

The following statements can be verified from committed code, tests, generated artifacts, and the
local interface:

- Built an independent local prototype for suitability-aware wealth and securities research.
- Adapted active clarification, explicit state, confidence boundaries, and evaluation ideas after
  a read-only review of Converge; no Converge source file was copied.
- Implemented a deterministic policy engine that distinguishes education, clarification, caution,
  refusal, and human review for declared prototype rules.
- Implemented tested deterministic calculations for return, volatility, drawdown, fees,
  concentration, exposure, scenarios, selected ratios, and comparison normalisation.
- Built a 13-document official PDF/HTML pack with file/chunk checksums, PDF-page and HTML-paragraph
  citations, version/freshness labels, conflict downgrade and exact-passage viewer.
- Created and ran 126 fixed-seed synthetic regression cases; the latest generated run passed
  126/126 with the denominators published in `EVALUATION_REPORT.md`.
- Created and ran 39 deterministic official citation-trace cases; the latest run passed 39/39
  across 13 source documents.
- Core demo and tests run without a paid API or API key.

Each statement should be scoped to **prototype**, **synthetic**, **offline**, or **committed test
suite** where applicable.

## Claims that must not be made

Do not claim or imply:

- real users, assets under management, account connections, trades, conversion, retention,
  revenue, paid usage, or financial loss avoided;
- real historical or forecast performance from the synthetic price paths;
- successful investment recommendations, alpha, risk-adjusted returns, or improved client wealth;
- approval, validation, deployment, partnership, or endorsement by any technology company, broker,
  bank, fund manager, regulator, exchange, issuer, or public information source;
- regulatory suitability compliance, investment-adviser status, legal review, or production-grade
  security/compliance;
- 100% accuracy on unseen questions, factual truth of all sources, or elimination of hallucination;
- independent human annotation, statistical significance, or usability improvement;
- copying or owning Converge's historical metrics, code, data, or commercial results;
- use of private, internal, paid, or institution-only data;
- that an optional model provider made the product decisions, calculations, or policy rules.

## Honest resume wording

Recommended:

> Built WealthGuard Proofline, a local React/FastAPI complement for securities
> assistants; implemented pre-answer evidence/version validation and post-answer bad-case
> governance, alongside information-value clarification, deterministic policy/calculation tools,
> citation validation and auditable response paths.

> Designed and ran a 126-case fixed-seed synthetic regression suite covering clarification,
> advice/execution boundaries, profile-product conflicts, citations, numerical consistency,
> stale-data warnings, refusal, and model-failure fallback; published metric definitions,
> denominators, ablations, failures, and limitations.

Avoid compressing the second statement to “100% accurate” or “zero hallucination.” Those phrases
discard the synthetic taxonomy scope and would be misleading.

## Known product and engineering limits

- Offline English/Chinese set with 13 official originals and four instrument fixtures.
- PDF extraction depends on embedded text; scanned or image-only sources need an OCR path.
- Instrument metadata can combine a real name with synthetic analytical assumptions.
- No authentication, durable database, access-control model, encryption design, or tamper-evident
  audit storage.
- No live market data, corporate-action adjustment, brokerage connection, or order path.
- No formal accessibility audit, penetration test, load test, legal review, or regulator review.
- Mock mode does not represent the behaviour of an arbitrary production LLM.
- Policy pattern coverage is intentionally finite and can produce false positives or negatives.
- Clarification priors and task relevance weights are declared product assumptions, not calibrated
  from user data.

## Human ownership

The user may view, correct, skip, or reset voluntary research context and must verify current
primary sources. Every real financial decision remains with the user and, where appropriate, a
qualified professional. The product should be stopped or escalated when the available evidence,
policy coverage, or user's circumstances exceed this prototype's boundary.
