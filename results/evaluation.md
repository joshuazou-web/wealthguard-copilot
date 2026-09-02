# Deterministic evaluation

Generated from `126` committed synthetic cases with seed `7319`.
This is a regression result, not real-user, investment-performance, or production evidence.

**Passed: 126/126; failed: 0.**

| metric | result | numerator / denominator |
| --- | ---: | ---: |
| `clarification_necessity_accuracy` | 1.000 | 40 / 40 |
| `clarification_question_utility` | 1.000 | 40 / 40 |
| `task_state_accuracy` | 1.000 | 120 / 120 |
| `citation_precision` | 1.000 | 165 / 165 |
| `citation_completeness` | 1.000 | 55 / 55 |
| `grounded_claim_rate` | 1.000 | 165 / 165 |
| `unsupported_claim_rate` | 0.000 | 0 / 165 |
| `numerical_consistency` | 1.000 | 55 / 55 |
| `stale_data_detection_rate` | 1.000 | 50 / 50 |
| `suitability_policy_violation_rate` | 0.000 | 0 / 45 |
| `correct_abstention_rate` | 1.000 | 5 / 5 |
| `correct_refusal_rate` | 1.000 | 15 / 15 |
| `prompt_injection_defense_rate` | 1.000 | 3 / 3 |
| `multi_turn_state_update_rate` | 1.000 | 2 / 2 |
| `source_conflict_detection_rate` | 1.000 | 1 / 1 |
| `missing_data_rejection_rate` | 1.000 | 1 / 1 |
| `schema_failure_fallback_rate` | 1.000 | 1 / 1 |
| `provider_unavailable_fallback_rate` | 1.000 | 1 / 1 |
| `regression_pass_rate` | 1.000 | 126 / 126 |

## Executed ablation baselines

Each baseline is evaluated only on the committed slice its removed control is required to pass.

| baseline | result | slice |
| --- | ---: | --- |
| `no_active_clarification` | 0/40 | Cases requiring a decision-relevant clarification |
| `no_policy_engine` | 0/40 | Refusal, human-review, profile-conflict, and advice-boundary cases |
| `no_deterministic_calculation_tools` | 0/55 | Cases requiring independently reproducible calculations |

## Failures

No failing committed cases in this run.

## Interpretation limits

- Cases are synthetic and taxonomy-driven; they do not estimate open-world user behaviour.
- Citation metrics validate identifiers and product control flow, not independent truth of every source.
- Suitability rules are prototype product policies, not jurisdiction-specific legal compliance.
- Synthetic price paths test arithmetic only and must not be represented as historical returns.
