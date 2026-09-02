# AI boundaries

## Purpose

WealthGuard uses a language-model boundary without granting the model control of financial
decisions. Default mock mode provides the complete local demonstration with no API key.

## Responsibility split

| Function | LLM allowed? | Authoritative component |
| --- | ---: | --- |
| Intent language cues | Assist only | Versioned classifier and test cases |
| Profile state and overrides | No | State manager |
| Clarification priority | No | Forward simulation and information-value planner |
| Suitability/product policy | No | Deterministic policy engine |
| Document retrieval | No | Local retrieval index |
| Return, fee, risk, exposure math | No | Deterministic calculation tools |
| Evidence phrasing | Yes | Provider interface plus schema validation |
| Citation validity | No | Evidence validator |
| Answer/caution/abstain/refuse mode | No | Policy and confidence controller |
| Real-world financial decision | No | Human user and qualified adviser where appropriate |

## Provider controls

- A common provider interface prevents model names from entering business logic.
- Mock mode is deterministic and is the default.
- Optional OpenAI-compatible mode requires explicit environment configuration.
- No key is committed; `.env.example` contains variable names only.
- Provider, model, prompt version, and relevant parameters are recorded in the audit event.
- Structured output is validated by Pydantic. Invalid structure or unknown citation IDs triggers a
  safe fallback and policy trace rather than silent acceptance.

## Prohibited outputs and actions

The product must not:

- place, route, simulate completion of, or claim to complete a real trade;
- connect to or request credentials for a brokerage account;
- issue personalised buy, sell, hold, position-size, or guaranteed-return instructions;
- predict a security price or imply future performance from synthetic series;
- treat education-oriented profile context as formal regulatory suitability certification;
- reveal sensitive data, comply with a request to bypass policy, or follow instructions embedded
  in retrieved content;
- describe a model response as a licensed adviser conclusion.

## Degraded modes

- **Missing research context:** ask the highest-value question or provide general education only.
- **Unknown/invalid citation:** remove the unsupported claim and record `INVALID_CITATION`.
- **No retrievable evidence:** abstain from factual research conclusions.
- **Stale source:** retain the dated fact only with a prominent stale warning; do not present it as
  current.
- **Conflicting sources:** surface the conflict and request human review; do not resolve it through
  model confidence alone.
- **Provider unavailable/schema failure:** use bounded deterministic fallback text. Policy,
  calculations, retrieval, and audit remain available.
- **Distress or gambling language:** stop product research and present a human-review pathway.

## Disclosure

Every primary surface and research response carries: “For educational and research purposes only.
Not investment advice.” This sentence is a disclosure, not a substitute for the technical controls
above.

