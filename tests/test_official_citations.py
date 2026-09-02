from __future__ import annotations

import hashlib
from html import escape

import pytest
from fastapi.testclient import TestClient
from wealthguard.api import app
from wealthguard.evidence import detect_conflicts
from wealthguard.models import DocumentChunk, PolicyOutcome, ResearchRequest
from wealthguard.official_ingestion import ROOT, load_chunks, load_manifest, verify_source_file
from wealthguard.retrieval import Retriever
from wealthguard.service import WealthGuardService

SOURCES = load_manifest()
CHUNKS = load_chunks()
BY_DOCUMENT = {source.document_id: [] for source in SOURCES}
for _chunk in CHUNKS:
    BY_DOCUMENT[_chunk.document_id].append(_chunk)
OFFICIAL_RETRIEVER = Retriever([], chunks=CHUNKS)

CITATION_CASES = [
    pytest.param(source.document_id, index, id=f"{source.authority}-{source.document_id}-{index}")
    for source in SOURCES
    for index in (0, len(BY_DOCUMENT[source.document_id]) // 2, len(BY_DOCUMENT[source.document_id]) - 1)
]


@pytest.mark.parametrize(("document_id", "chunk_index"), CITATION_CASES)
def test_official_citation_trace_is_complete(document_id: str, chunk_index: int) -> None:
    source = next(item for item in SOURCES if item.document_id == document_id)
    chunk = BY_DOCUMENT[document_id][chunk_index]
    assert chunk.document_id == source.document_id
    assert chunk.source_url == source.source_url
    assert chunk.document_sha256 == source.sha256
    assert hashlib.sha256(chunk.text.encode("utf-8")).hexdigest() == chunk.text_sha256
    assert chunk.page_number or chunk.paragraph_start
    assert chunk.published_at or chunk.version_status == "undated"
    assert OFFICIAL_RETRIEVER.validate_citations([chunk.chunk_id])


def test_manifest_has_required_authorities_types_and_document_count() -> None:
    assert len(SOURCES) >= 12
    assert {source.authority for source in SOURCES} == {"SEC", "HKEX", "SZSE", "CSRC"}
    assert {"annual_report", "fund_etf_prospectus", "regulatory_investor_education"} <= {
        source.document_type for source in SOURCES
    }


def test_modified_official_file_fails_checksum(tmp_path) -> None:
    source = SOURCES[0]
    changed = tmp_path / source.raw_filename
    changed.write_bytes((ROOT / source.raw_path).read_bytes() + b"changed")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify_source_file(source, changed)


def test_open_original_locator_contains_exact_passage_and_metadata() -> None:
    chunk = next(item for item in CHUNKS if item.page_number and len(item.text) > 40)
    response = TestClient(app).get("/api/evidence/open", params={"chunk_id": chunk.chunk_id})
    assert response.status_code == 200
    assert escape(chunk.text) in response.text
    assert chunk.document_sha256 in response.text
    assert f"Page {chunk.page_number}" in response.text


def _conflict_chunk(base: DocumentChunk, suffix: str, value: str) -> DocumentChunk:
    text = f"Official filing states the same-period reported amount as {value}."
    return base.model_copy(
        update={
            "chunk_id": f"TEST-CONFLICT-{suffix}:para1-1:c1",
            "document_id": f"TEST-CONFLICT-{suffix}",
            "title": f"Conflict source {suffix}",
            "text": text,
            "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "structured_facts": {"reported_amount@FY2025": value},
        }
    )


def test_two_document_numeric_conflict_forces_caution() -> None:
    base = next(item for item in CHUNKS if item.instrument_id == "AAPL")
    first = _conflict_chunk(base, "A", "416161")
    second = _conflict_chunk(base, "B", "415000")
    evidence = Retriever([], chunks=[first, second]).search("AAPL reported amount FY2025", ["AAPL"])
    assert detect_conflicts(evidence)
    response = WealthGuardService(research_chunks=[first, second]).research(
        ResearchRequest(query="Research AAPL reported amount for FY2025", instrument_ids=["AAPL"])
    )
    assert response.outcome == PolicyOutcome.CAUTION
    assert any(hit.rule_id == "SOURCE_CONFLICT" for hit in response.policy.hits)


def test_older_versions_and_stale_sources_are_exposed() -> None:
    evidence = OFFICIAL_RETRIEVER.search("Apple total net sales", ["AAPL"], limit=4)
    assert {item.version_status for item in evidence} >= {"latest", "older_version"}
    old = next(item for item in CHUNKS if item.document_id == "CSRC-SECURITIES-INVESTMENT-FUND-LAW-2012")
    result = Retriever([], chunks=[old]).search("investment fund law", [], limit=1)[0]
    assert result.freshness == "stale"
