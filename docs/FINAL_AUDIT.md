# Final delivery audit

Audit date: 2026-09-02

## Repository integrity

- WealthGuard Proofline is an independent Git repository; this audit does not claim Tencent or brokerage affiliation.
- Converge remained at `b371720f5a02afc5791fdbd8887927d6452f923e` with no tracked diff.
- The pre-existing untracked Converge file `results/codex-verification.json` remained unmodified and
  untracked.
- No Converge source, `.git` directory, result artifact, cache, key, or machine configuration was
  copied.
- A repository scan found no absolute user path, private-key marker, API token pattern, or named
  company branding prohibited by the product brief.

## Functional acceptance

- Mock mode runs without an API key.
- The end-to-end API journey returned clarification, completed bounded research, three evidence
  cards, five calculation outputs, comparison, portfolio calculations, audit events, and evaluation
  results.
- Profile fields can be changed or withdrawn; computed task/missing-context state is persisted.
- Intent override is recorded in the audit trail.
- Advice/execution boundaries and profile-product conflicts are deterministic.
- Document ingestion validates IDs, HTTPS provenance, date order, and checksum.
- Evidence validation rejects unknown citations and detects conflicting structured facts.
- Return, volatility, drawdown, fee, concentration, exposure, scenario, ratio, and normalisation
  calculations are deterministic and tested.
- Portfolio view includes sector, region, currency, synthetic volatility, synthetic drawdown, and a
  declared simple scenario without allocation instructions.

## Verification evidence

`scripts/verify.ps1` completed successfully:

- Ruff format check: passed for 21 Python files.
- Ruff static checks: passed.
- Python tests: 25 passed.
- Deterministic evaluation: 126/126 committed synthetic cases passed, seed 7319.
- Frontend TypeScript check: passed.
- Vite production build: passed; 30 modules transformed.

One dependency-level deprecation warning is emitted by FastAPI's current `TestClient` compatibility
layer. It does not fail the suite; upgrading the underlying test transport should be handled when
the FastAPI/Starlette ecosystem completes that transition.

## Visual acceptance

The running product was tested in headless Chrome at 1440×1000, 1366×768, and 1024×768.

- Research, comparison, portfolio, evidence, audit, and evaluation views loaded with content.
- No horizontal document overflow was detected.
- No interactive element was clipped beyond the viewport.
- No browser console or page error remained.
- Screenshots in `docs/media/` were captured from the running local product.

## Truth audit

- Default public material is retained as checksum-verified official PDF/HTML with source, version,
  dates and page/paragraph locations; synthetic fixtures remain separately labelled.
- The 39-case official citation traceability run passed 39/39 across 13 files.
- Synthetic products, prices, exposures, profiles, portfolios, scenarios, and evaluations are
  labelled as synthetic.
- The 126/126 result is presented only as fixed-taxonomy regression coverage with denominators and
  limitations.
- The product makes no claim of real users, trading, assets, financial performance, institutional
  validation, regulatory compliance, deployment, or commercial impact.
- Resume-safe and prohibited claims are recorded in `TRUTH_AND_LIMITATIONS.md`.

## Open limitations

The prototype remains offline, English-heavy, unauthenticated, process-local, and unreviewed by a
financial institution, legal team, regulator, or independent annotator. It has no live market data,
brokerage connection, durable audit store, source-span ingestion pipeline, load/security test, or
production deployment. These are declared product boundaries, not completed capabilities.
