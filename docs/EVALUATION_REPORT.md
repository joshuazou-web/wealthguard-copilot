# Evaluation report

## Scope and latest result

The latest verified run evaluated **126 committed synthetic cases** with seed `7319`: **126 passed,
0 failed**. These results demonstrate deterministic regression behaviour over a declared taxonomy.
They do not measure real-user utility, open-world accuracy, production reliability, legal
compliance, investment performance, conversion, retention, or financial outcomes.

Generated machine-readable artifacts live in `results/evaluation.json` and
`results/evaluation.md`. A separate official-source traceability artifact contains **39/39 passed
cases across 13 documents**. Regenerate both with:

```powershell
.\.venv\Scripts\python.exe -m wealthguard.evaluation.runner
.\.venv\Scripts\python.exe scripts\run_citation_evaluation.py
```

## Official citation traceability evaluation

`results/citation_evaluation.json` selects the first, middle and final chunk from every official
document: 39 fixed cases. Each verifies the parent file checksum, chunk checksum, document/source
link, date-or-explicit-undated state, exact page/paragraph location and non-empty extracted span.
The latest run passed 39/39. This is an integrity/traceability test, not evidence of semantic
entailment quality for arbitrary generated claims.

## Construction

Cases are generated deterministically by `backend/wealthguard/evaluation/cases.py`; no case is
removed based on its outcome. The suite contains:

| Category | Cases | Main assertions |
| --- | ---: | --- |
| Advice-like clarification | 20 | Missing context detected; selected field is relevant |
| Comparison clarification | 10 | Horizon/liquidity context requested |
| Portfolio clarification | 10 | Risk/concentration/currency context requested |
| Refusal | 15 | Execution, guarantee, bypass, and sensitive-data controls |
| Human review | 5 | Distress/gambling path |
| Education | 10 | Informational outcome, evidence, calculations |
| Source grounding | 15 | Dated evidence, citations, calculations |
| Profile-product conflict | 10 | Caution rather than unqualified answer |
| Advice boundary | 10 | Educational reframe rather than recommendation |
| Numerical | 10 | Independent deterministic recomputation |
| Invalid citation / abstention | 5 | Unknown citation removed and response downgraded |
| Intent override | 1 | Changed task is recorded and persisted across turns |
| Multi-turn completion | 1 | Missing context is supplied and the research path updates |
| Source conflict | 1 | Conflicting structured facts are surfaced and downgraded |
| Missing calculation data | 1 | Deterministic tool rejects insufficient input |
| Provider schema failure | 1 | Bounded mock fallback and disclosure |
| Provider unavailable | 1 | Bounded mock fallback and disclosure |

The English and Chinese prompts are hand-authored synthetic examples. Profile values, product
fixtures, price paths, and portfolio inputs are synthetic. Default public evidence comes from the
checksum-verified official originals listed in `DATA_SOURCES.md`.

## Metrics and formulas

For ordinary accuracy/rate metrics:

`metric = successful applicable cases or claims / all applicable cases or claims`

`unsupported_claim_rate` and `suitability_policy_violation_rate` are defect rates, so lower is
better. Denominators include only cases where the behaviour is applicable.

| Metric | Latest | Numerator / denominator | Meaning in this suite |
| --- | ---: | ---: | --- |
| Clarification necessity accuracy | 1.000 | 40 / 40 | A question was selected when required |
| Clarification question utility | 1.000 | 40 / 40 | Selected field belonged to the declared relevant missing set |
| Task-state accuracy | 1.000 | 120 / 120 | Intent matched the committed label on single-turn cases |
| Citation precision | 1.000 | 165 / 165 | Emitted citation ID existed in the register |
| Citation completeness | 1.000 | 55 / 55 | Evidence and a cited claim were both present |
| Grounded-claim rate | 1.000 | 165 / 165 | Claim was cited or explicitly synthetic |
| Unsupported-claim rate | 0.000 | 0 / 165 | Claim had unknown or missing evidence |
| Numerical consistency | 1.000 | 55 / 55 | Core values matched independent recomputation |
| Stale-data detection rate | 1.000 | 60 / 60 | Review-date/stale/future evidence added a date limitation |
| Suitability-policy violation rate | 0.000 | 0 / 45 | Restricted case incorrectly returned informational |
| Correct abstention rate | 1.000 | 5 / 5 | Invalid citations were removed and response downgraded |
| Correct refusal rate | 1.000 | 15 / 15 | Declared refusal request was refused |
| Prompt-injection defence rate | 1.000 | 3 / 3 | Explicit bypass request was refused |
| Multi-turn state update rate | 1.000 | 2 / 2 | Task override and profile completion persisted correctly |
| Source-conflict detection rate | 1.000 | 1 / 1 | Conflict was surfaced with a caution outcome |
| Missing-data rejection rate | 1.000 | 1 / 1 | Insufficient calculation input raised a controlled error |
| Schema-failure fallback rate | 1.000 | 1 / 1 | Schema failure used and disclosed bounded fallback |
| Provider-unavailable fallback rate | 1.000 | 1 / 1 | Provider failure used and disclosed bounded fallback |
| Regression pass rate | 1.000 | 126 / 126 | Every assertion for the case passed |

Citation precision here validates registered identifiers and service control flow. It is not an
independent factual audit of every public source statement.

## Executed ablation baselines

Each ablation is run against only the committed slice that requires its removed control. The
baseline definitions are deliberately simple and are generated by the same runner:

| Ablation | Result | Relevant slice | Interpretation |
| --- | ---: | ---: | --- |
| No active clarification | 0 / 40 | 40 | An always-answer assistant cannot select a required question |
| No policy engine | 0 / 40 | 40 | An always-informational RAG cannot produce required refusal, human review, caution, or advice reframe |
| No deterministic calculation tools | 0 / 55 | 55 | An answer that omits tools cannot pass numerical consistency |

These are component ablations, not a comparison against commercial models or human advisers.
Their purpose is to show that the acceptance cases actually depend on the named control.

## Failure analysis

The latest committed run has no failing cases. During implementation, intent precedence caused
advice/execution language embedded in research-like prompts to be under-classified. The fix made
execution and advice boundary cues precede comparison, education, portfolio, and general research
cues, then re-ran the complete suite. This development observation is not included as a measured
production incident.

The evaluation artifact never hides failures: `failed` and the complete `failures` list are
generated in JSON. A future regression must remain visible until the implementation or declared
test expectation is independently corrected.

## Known limitations

- Cases are taxonomy-driven and share vocabulary with the implemented rules.
- Labels were not independently double-annotated; inter-rater agreement is unknown.
- The suite is not multilingual beyond a small set of Chinese examples.
- Source validity is not checked over the network during the offline run.
- Retrieval measures are indirect; there is no independently judged recall benchmark.
- The mock provider avoids non-determinism and cannot estimate real-model hallucination rates.
- Policy rules are not jurisdiction-specific and have not been reviewed by a regulator or
  financial institution.
- The three ablations isolate required controls but do not estimate the quality of a strong
  alternative end-to-end system.

## Next evaluation work

1. Build a held-out set authored by a second annotator and freeze it before implementation changes.
2. Report confusion matrices, calibration, inter-rater agreement, and bootstrap intervals.
3. Add source-span entailment review and retrieval-recall labels.
4. Test paraphrase robustness, mixed-language prompts, indirect injection, and multi-turn overrides.
5. Evaluate real providers with pinned model/prompt versions while preserving the mock baseline.
6. Run moderated usability studies only with consent and report sample size and method.
