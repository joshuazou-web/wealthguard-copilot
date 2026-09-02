# Dependency licence review

Reviewed from the installed Python package metadata and `pnpm licenses list --json` on
2026-09-02. This is an engineering inventory, not legal advice.

## Direct Python dependencies

| Package | Verified installed version | Declared licence |
| --- | ---: | --- |
| FastAPI | 0.141.1 | MIT |
| Uvicorn | 0.52.4 | BSD-3-Clause |
| Pydantic | 2.13.5 | MIT |
| HTTPX (development) | 0.28.1 | BSD-3-Clause |
| pytest (development) | 8.4.2 | MIT |
| pytest-cov (development) | 6.3.0 | MIT |
| Ruff (development) | 0.16.5 | MIT |

## Frontend dependency tree

The installed pnpm tree reported MIT, Apache-2.0, BSD-3-Clause, ISC, and CC-BY-4.0 packages. Direct
runtime/build dependencies include React/React DOM (MIT), Vite and its React plugin (MIT), and
TypeScript (Apache-2.0). Exact resolved versions are retained in `frontend/pnpm-lock.yaml`.

## Converge provenance

The inspected Converge repository declares the MIT License, copyright 2026 Josh Zou. No Converge
source file or bundled dependency was copied into WealthGuard. Reused architectural ideas are
recorded in `CONVERGE_MIGRATION.md`; therefore no copied-source notice is required in the current
codebase. Any future source-level reuse must preserve the relevant licence and attribution.

Before redistribution, re-run the inventory against the locked environment and review source/data
terms separately from software package licences.

