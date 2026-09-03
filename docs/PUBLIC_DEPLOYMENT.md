# Public web deployment

WealthGuard ships as one Docker image: Vite produces the responsive frontend, and FastAPI serves
both that build and the same-origin API. The included `render.yaml` describes one Docker web
service with `/health` as its health check. No API key or paid market-data service is required.

## Before deployment

Run the complete local gate:

```powershell
.\.venv\Scripts\python.exe -m ruff format --check backend tests scripts
.\.venv\Scripts\python.exe -m ruff check backend tests scripts
.\.venv\Scripts\python.exe -m pytest
pnpm --dir frontend typecheck
pnpm --dir frontend build
$env:WEALTHGUARD_QA_URL="http://127.0.0.1:8000"
pnpm --dir frontend qa:visual
```

The visual check launches installed Chrome at 390×844 and 1440×1000, rejects horizontal mobile
overflow, runs two research traces, opens an exact cited passage, records feedback, and verifies
that the browser-local study data persists.

## Render deployment

1. Push this repository to a private GitHub repository.
2. Sign in to Render and authorize access to that repository.
3. Create a Blueprint from the root `render.yaml`.
4. Wait for the Docker build and `/health` check to pass.
5. Open the assigned `onrender.com` URL on desktop and mobile, then rerun the smoke path below.

Render's Blueprint specification supports Docker services, `dockerfilePath`, `healthCheckPath`,
and commit-triggered deploys. Free web services may spin down after inactivity, so a cold first
request should be recorded as hosting friction—not confused with product latency.

## Post-deploy smoke path

1. Confirm `/health` returns `status: ok`.
2. Ask `Is SPY suitable for me?` and confirm a clarification is shown.
3. Ask `What does SPY invest in and what are its stated risks?`.
4. Open one exact cited passage and verify the page/paragraph, publication date, and checksum.
5. Mark the trace `Useful` and reload; the 14-day panel must still show the session.
6. Open Review & audit. Only the current browser's random session should appear.
7. Request `/api/audit` without a session. It must return HTTP 422.

## Data and privacy boundary

- Voluntary profile, last question, selected instruments, and the 14-day study log are stored in
  browser `localStorage`; they are not a user account or cloud suitability record.
- The backend keeps short-lived session traces in process memory. They disappear on restart.
- A random browser session ID prevents ordinary cross-visitor mixing, but this prototype has no
  authentication and must not receive identity data, account numbers, exact holdings, or trades.
- Public access does not imply endorsement by an issuer, exchange, regulator, brokerage, Tencent,
  WeChat, or any other institution.
