# Data dictionary

## User research profile

All fields are optional research context. They are not identity data or formal suitability answers.

| Field | Type | Meaning |
| --- | --- | --- |
| `research_goal` | string/null | User's current learning or research objective |
| `investment_horizon` | enum-like string/null | When the researched money may be needed |
| `liquidity_need` | enum-like string/null | Expected speed of access |
| `loss_tolerance` | enum-like string/null | Self-described tolerance band for research framing |
| `investment_experience` | enum-like string/null | Familiarity with market products |
| `product_knowledge` | enum-like string/null | Familiarity with the current product type |
| `concentration_preference` | enum-like string/null | Desired sensitivity to concentration warnings |
| `currency_exposure` | enum-like string/null | Preference for foreign-currency disclosure |
| `information_preference` | enum-like string/null | Plain, balanced, or technical explanation |
| `current_task` | string/null | Latest classified task summary |
| `missing_information` | string list | Context still required by the current policy path |
| `confidence` | 0–1 number | Task-state confidence, not investment confidence |
| `last_updated_at` | UTC timestamp | State update time |

## Instrument fixture

| Field | Meaning |
| --- | --- |
| `instrument_id`, `symbol`, `name` | Stable demo identifier and display labels |
| `instrument_type`, `issuer`, `currency`, `region` | Product metadata |
| `risk_level` | Prototype ordinal risk assumption from 1–5 |
| `complexity` | Standard/complexity flag used by prototype policy |
| `min_horizon_months`, `liquidity_days` | Demonstration policy inputs |
| `expense_ratio` | Decimal annual expense assumption |
| `sectors`, `regions` | Weight maps that must each sum to one |
| `as_of` | Date attached to the metadata fixture |
| `data_status` | Public-paraphrase or synthetic-fixture provenance label |

Instrument-level fields can mix a real public product name with synthetic analytical assumptions;
the current fixture therefore defaults to `synthetic_demo_data`. Source-backed facts live in
documents and claims, where provenance can be expressed more precisely.

## Research document and evidence

| Field | Meaning |
| --- | --- |
| `document_id` | Stable source-note identifier |
| `instrument_id` | Optional associated instrument |
| `document_type` | Prospectus, annual report, education note, or synthetic disclosure |
| `source_name`, `source_url` | Human-readable source and original location |
| `published_at`, `retrieved_at` | Source date and collection date |
| `content`, `key_facts`, `structured_facts` | Curated paraphrase, review facts, and comparable fact values |
| `data_status` | `public_source_paraphrase` or `synthetic_demo_data` |
| `checksum` | SHA-256 of the committed note text |
| `score` | Local retrieval relevance score |
| `freshness` | `current_for_demo`, `review_date`, `stale`, or `future_dated` date label |

When two retrieved documents attach different values to the same instrument and structured-fact
key, the evidence validator emits a conflict containing the fact key, values, and document IDs.
The service downgrades the result to caution and requires date/version review.

## Policy and clarification

`Intent` contains education, research, comparison, portfolio analysis, personalised advice, and
trade execution. `PolicyOutcome` contains informational, clarification required, educational only,
caution, refuse, and human review.

A clarification candidate records its field, natural-language question, information-value score,
policy-outcome entropy, answer entropy, simulated outcomes, and explanation.

## Calculation result

Every result includes `metric`, numeric or structured `value`, `unit`, `formula`, explicit
`assumptions`, and `data_status`. A displayed number without this structure is a defect.

## Audit event

An audit event records timestamp, session, query, intent, policy outcome, profile changes,
clarification trace, rule hits, evidence IDs, calculation metric names, provider, model, and prompt
version. The current store is process-local and is not a tamper-evident production audit system.
