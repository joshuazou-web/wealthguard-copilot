"""FastAPI application for the local WealthGuard demo."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

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


@app.middleware("http")
async def public_demo_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "provider": service.provider.name, "disclaimer": DISCLAIMER}


@app.get("/api/instruments")
def instruments() -> list[dict]:
    return [item.model_dump(mode="json") for item in service.list_instruments()]


@app.get("/api/documents")
def research_documents() -> list[dict]:
    return [item.model_dump(mode="json") for item in service.documents]


@app.get("/api/evidence/open", response_class=HTMLResponse)
def open_evidence(chunk_id: str = Query(min_length=3, max_length=300)) -> str:
    chunk = service.retriever.chunk(chunk_id)
    if chunk is None:
        raise HTTPException(status_code=404, detail="unknown evidence chunk")
    location = (
        f"Page {chunk.page_number}"
        if chunk.page_number
        else (f"Paragraphs {chunk.paragraph_start}–{chunk.paragraph_end}")
    )
    if chunk.source_line_start:
        location += f" · source lines {chunk.source_line_start}–{chunk.source_line_end}"
    official_url = chunk.source_url + (f"#page={chunk.page_number}" if chunk.page_number else "")
    raw_link = (
        f'<a href="/api/sources/{escape(chunk.document_id)}/raw#page={chunk.page_number}">Open cached PDF at page</a>'
        if chunk.page_number
        else ""
    )
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{escape(chunk.title)}</title>
    <style>body{{font:16px/1.6 system-ui;max-width:900px;margin:40px auto;padding:0 24px;color:#17312d}}
    .meta{{color:#60736f}} pre{{white-space:pre-wrap;background:#f2f7f5;padding:24px;border-left:4px solid #157a6e}}
    a{{color:#087668;margin-right:20px}}</style></head><body><h1>{escape(chunk.title)}</h1>
    <p class="meta">{escape(chunk.document_id)} · {escape(location)} · published
    {escape(str(chunk.published_at or "not stated"))}<br>
    version: {escape(chunk.version)} · SHA-256: {escape(chunk.document_sha256)}</p>
    <pre>{escape(chunk.text)}</pre><p>{raw_link}<a href="{escape(official_url)}">Open official original</a></p>
    <p class="meta">For educational and research purposes only. Not investment advice.</p></body></html>"""


@app.get("/api/sources/{document_id}/raw")
def raw_source(document_id: str) -> FileResponse:
    source = next((item for item in service.official_sources if item.document_id == document_id), None)
    if source is None or source.media_type != "application/pdf":
        raise HTTPException(status_code=404, detail="cached PDF not found")
    path = Path(__file__).resolve().parents[2] / source.raw_path
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=source.raw_filename,
        content_disposition_type="inline",
    )


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
def audit(
    session_id: str = Query(min_length=8, max_length=80),
    limit: int = Query(default=50, ge=1, le=500),
) -> list[dict]:
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


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONTEND_DIST.exists():
    assets = FRONTEND_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str) -> FileResponse:
        requested = (FRONTEND_DIST / path).resolve()
        if path and requested.is_relative_to(FRONTEND_DIST.resolve()) and requested.is_file():
            return FileResponse(requested)
        return FileResponse(FRONTEND_DIST / "index.html")
