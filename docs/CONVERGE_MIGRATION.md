# Converge migration record

## Source inspected

- Repository: `joshuazou-web/techjam-converge`
- Commit inspected: `b371720f5a02afc5791fdbd8887927d6452f923e`
- Licence: MIT for repository source; organizer data excluded.
- Source repository role during this project: read-only reference.

## Concepts reused

| Converge concept | WealthGuard adaptation |
| --- | --- |
| Replayable user transcript | Explicit research profile and task-state history |
| Forward user simulation | Simulate policy outcomes for possible answers |
| Expected information gain | Ask the missing field most likely to change the safe research path |
| Confidence-gated slate | Clarify, answer, caution, abstain, refuse, or route to human review |
| Intent override | Replace changed horizon, goal, liquidity, or risk context and log the change |
| Trace per turn | Audit question utility, policy hits, evidence, calculations, and response mode |
| Ablation and robustness tools | Compare full system with no-clarification/no-policy baselines |

## Not reused

- Hackathon participant kit, evaluator, catalog, results, and Amazon-derived data.
- Shopping-specific NLU templates, product cards, popularity prior, BM25/FTS catalog ranking,
  rank/turn score optimization, conversion inference, and slate-width policy.
- Existing source files. The first implementation is written independently so finance-specific
  assumptions remain visible and the repositories do not share runtime dependencies.

## Code provenance

No Converge source file is copied into this repository. The shared contribution is architectural:
stateful intent modelling, information-value clarification, confidence gating and evidence-driven
evaluation. Any later source-level reuse must be recorded here with file-level attribution.

## Independence controls

- Separate directory, Git metadata, package name, test suite, datasets and runtime configuration.
- No `.git`, `.kit`, result artifact, key, cache or machine path copied from Converge.
- Final verification compares Converge `HEAD`, tracked diff and pre-existing untracked state.

