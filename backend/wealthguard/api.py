"""FastAPI application for the local WealthGuard demo."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .models import CompareRequest, PortfolioRequest, ResearchRequest, UserProfile
from .service import DISCLAIMER, WealthGuardService

app = FastAPI(
    title="WealthGuard Copilot",
    version="0.1.0",
    description="Suitability-aware wealth and securities research prototype.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
service = WealthGuardService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": service.provider.name, "disclaimer": DISCLAIMER}


@app.get("/api/instruments")
def instruments() -> list[dict]:
    return [item.model_dump(mode="json") for item in service.list_instruments()]


@app.get("/api/documents")
def research_documents() -> list[dict]:
    return [item.model_dump(mode="json") for item in service.documents]


@app.post("/api/research")
def research(request: ResearchRequest) -> dict:
    return service.research(request).model_dump(mode="json")


@app.post("/api/compare")
def compare(request: CompareRequest) -> dict:
    try:
        return service.compare(request).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/portfolio")
def portfolio(request: PortfolioRequest) -> dict:
    try:
        return service.portfolio(request).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/audit")
def audit(session_id: str | None = None, limit: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    return [event.model_dump(mode="json") for event in service.store.audit(session_id, limit)]


@app.get("/api/profile/{session_id}")
def get_profile(session_id: str) -> dict:
    return service.store.profile(session_id).model_dump(mode="json")


@app.put("/api/profile/{session_id}")
def update_profile(session_id: str, profile: UserProfile) -> dict:
    updated, changes = service.store.update_profile(session_id, profile)
    return {"profile": updated.model_dump(mode="json"), "changes": changes}


@app.delete("/api/profile/{session_id}")
def reset_profile(session_id: str) -> dict:
    return service.store.reset_profile(session_id).model_dump(mode="json")


@app.get("/api/evaluation")
def evaluation() -> dict:
    path = Path(__file__).resolve().parents[2] / "results" / "evaluation.json"
    if not path.exists():
        return {"status": "not_run", "message": "Run: python -m wealthguard.evaluation.runner"}
    return json.loads(path.read_text(encoding="utf-8"))
