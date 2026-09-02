# Suitability and research-boundary policy

## Status

This is a deterministic policy pack for a product prototype. It is not a legal opinion, regulated
suitability assessment, fiduciary process, compliance certification, or substitute for a licensed
professional's judgement.

## Outcomes

| Outcome | Meaning |
| --- | --- |
| `informational` | Bounded education or sourced research can proceed |
| `clarification_required` | Missing context could materially change the safe path |
| `educational_only` | Reframe the request as education/research; do not personalise a recommendation |
| `caution` | Context and product characteristics conflict; explain the conflict |
| `refuse` | Do not satisfy the requested action or claim |
| `human_review` | Stop the research flow and surface a supportive human pathway |

## Pattern controls

| Rule | Trigger class | Result |
| --- | --- | --- |
| `TRADE_EXECUTION` | Request to place/execute an order | Refuse |
| `GUARANTEED_RETURN` | Guaranteed, loss-free, or “sure profit” language | Refuse |
| `POLICY_BYPASS` | Attempt to ignore or bypass safeguards | Refuse |
| `SENSITIVE_DATA` | Request for accounts, passwords, identity, or private data | Refuse |
| `FINANCIAL_DISTRESS` | Severe distress, borrowing everything, or gambling recovery | Human review |
| `MINOR` | Explicit minor-facing request | Educational only |

English and Chinese phrases are represented in the prototype tests. They are examples rather than
a comprehensive language-safety classifier.

## Profile-product controls

- `HORIZON_CONFLICT`: research horizon is shorter than the fixture's minimum horizon assumption.
- `LIQUIDITY_CONFLICT`: access is needed within days but the fixture has a longer liquidity window.
- `LOSS_TOLERANCE_CONFLICT`: product risk materially exceeds the stated tolerance band.
- `COMPLEXITY_KNOWLEDGE_GAP`: a complex product is paired with limited experience.
- `MISSING_RESEARCH_CONTEXT`: required fields are absent for comparison, portfolio, or advice-like
  framing.
- `ADVICE_REFRAME`: a personalised recommendation is converted to evidence-based research.

## Required context

- Education, general research, and refused execution: no profile field is mandatory.
- Comparison: horizon and liquidity.
- Portfolio analysis: loss tolerance, concentration preference, and currency preference.
- Advice-like question: horizon, liquidity, and loss tolerance; experience and product knowledge
  are additionally requested for complex or highest-risk fixtures.

Users can skip non-essential questions. Context is voluntary, visible, editable, and resettable.
It is not used to identify the user.

## Clarification selection

For every missing candidate field, the planner simulates a small declared set of possible answers
through the policy engine. The score combines:

`task relevance × (policy-outcome entropy + 0.25 × answer entropy)`

This score is a transparent prioritisation heuristic, not learned suitability logic. Candidate
answers and priors are product assumptions and are documented in code.

## Reviewer checklist

1. Did a high-risk pattern short-circuit the flow?
2. Was only relevant profile context requested?
3. Is the selected clarification trace visible?
4. Were profile/product conflicts retained in the response?
5. Did any model text override a deterministic outcome?
6. Does the audit event contain the fired rule IDs?
7. Does the result avoid buy/sell/hold, sizing, performance promises, and execution?

