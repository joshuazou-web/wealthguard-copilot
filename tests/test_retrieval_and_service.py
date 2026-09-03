from __future__ import annotations

import hashlib

import pytest
from fastapi.testclient import TestClient
from wealthguard.api import app
from wealthguard.evidence import detect_conflicts
from wealthguard.fixtures import documents
from wealthguard.ingestion import ingest_documents
from wealthguard.models import PolicyOutcome, ResearchRequest, UserProfile
from wealthguard.retrieval import Retriever
from wealthguard.service import WealthGuardService


def test_document_checksums_and_sources() -> None:
    for document in documents():
        assert len(document.checksum) == 64
        assert document.source_url.startswith("https://")
        assert document.published_at <= document.retrieved_at


def test_retrieval_boosts_selected_instrument() -> None:
    evidence = Retriever(documents()).search("fees and risks", ["SPY"])
    assert evidence
    assert evidence[0].document_id == "SEC-SPY-497-2026"


def test_ingestion_rejects_changed_content_and_conflicts_downgrade_response() -> None:
    source = documents()[0]
    invalid = source.model_copy(update={"content": source.content + " changed"})
    with pytest.raises(ValueError, match="checksum mismatch"):
        ingest_documents([invalid])

    conflicting_content = "Synthetic test note with a deliberately conflicting expense ratio."
    conflicting = source.model_copy(
        update={
            "document_id": "TEST-SPY-CONFLICT",
            "title": "Synthetic conflict fixture",
            "content": conflicting_content,
            "checksum": hashlib.sha256(conflicting_content.encode("utf-8")).hexdigest(),
            "structured_facts": {"expense_ratio": "0.001000"},
        }
    )
    evidence = Retriever([source, conflicting]).search("SPY expense ratio", ["SPY"])
    conflicts = detect_conflicts(evidence)
    assert conflicts and conflicts[0].fact_key == "expense_ratio"

    service = WealthGuardService(research_documents=[source, conflicting])
    response = service.research(
        ResearchRequest(
            session_id="conflict",
            query="Research SPY expense ratio",
            instrument_ids=["SPY"],
        )
    )
    assert response.outcome == PolicyOutcome.CAUTION
    assert response.conflicts
    assert any(hit.rule_id == "SOURCE_CONFLICT" for hit in response.policy.hits)


def test_service_clarifies_then_answers_with_updated_profile() -> None:
    service = WealthGuardService()
    first = service.research(
        ResearchRequest(session_id="flow", query="Is SPY suitable for me?", instrument_ids=["SPY"])
    )
    assert first.outcome == PolicyOutcome.CLARIFICATION_REQUIRED
    assert first.clarification and first.clarification.selected

    complete = UserProfile(investment_horizon="over_5_years", liquidity_need="flexible", loss_tolerance="high")
    second = service.research(
        ResearchRequest(
            session_id="flow",
            query="Is SPY suitable for me?",
            profile=complete,
            instrument_ids=["SPY"],
        )
    )
    assert second.outcome == PolicyOutcome.EDUCATIONAL_ONLY
    assert second.evidence and second.claims and second.calculations
    assert len(service.store.audit("flow")) == 2


def test_intent_override_is_recorded() -> None:
    service = WealthGuardService()
    service.research(
        ResearchRequest(
            session_id="override",
            query="Research SPY",
            profile=UserProfile(investment_horizon="over_5_years"),
            instrument_ids=["SPY"],
        )
    )
    service.research(
        ResearchRequest(
            session_id="override",
            query="Research SPY",
            profile=UserProfile(investment_horizon="under_1_year"),
            instrument_ids=["SPY"],
        )
    )
    newest = service.store.audit("override")[0]
    assert newest.profile_changes["investment_horizon"] == {
        "from": "over_5_years",
        "to": "under_1_year",
    }

    service.research(
        ResearchRequest(
            session_id="override",
            query="Compare SPY and WGBOND",
            profile=UserProfile(investment_horizon="under_1_year"),
            instrument_ids=["SPY", "WGBOND"],
        )
    )
    newest = service.store.audit("override")[0]
    assert newest.profile_changes["current_task"] == {
        "from": "research",
        "to": "compare",
    }


def test_profile_field_can_be_withdrawn_and_computed_state_is_saved() -> None:
    service = WealthGuardService()
    service.research(
        ResearchRequest(
            session_id="withdraw",
            query="Research SPY",
            profile=UserProfile(investment_horizon="over_5_years"),
            instrument_ids=["SPY"],
        )
    )
    response = service.research(
        ResearchRequest(
            session_id="withdraw",
            query="Is SPY suitable for me?",
            profile=UserProfile(investment_horizon=None),
            instrument_ids=["SPY"],
        )
    )
    saved = service.store.profile("withdraw")
    assert response.profile.investment_horizon is None
    assert saved.current_task == "personalised_advice"
    assert "investment_horizon" in saved.missing_information


def test_compare_and_portfolio_are_deterministic() -> None:
    client = TestClient(app)
    compare = client.post("/api/compare", json={"instrument_ids": ["SPY", "WGBOND"]})
    assert compare.status_code == 200
    assert "best" not in compare.json()
    portfolio = client.post(
        "/api/portfolio",
        json={
            "holdings": [
                {"instrument_id": "SPY", "weight": 0.6},
                {"instrument_id": "WGBOND", "weight": 0.4},
            ],
            "scenario_shock": -0.15,
        },
    )
    assert portfolio.status_code == 200
    assert sum(portfolio.json()["sector_exposure"].values()) == 1.0
    assert sum(portfolio.json()["currency_exposure"].values()) == 1.0
    metrics = {item["metric"] for item in portfolio.json()["calculations"]}
    assert {"portfolio_annualized_volatility", "portfolio_maximum_drawdown"} <= metrics


def test_health_and_no_key_research() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["provider"] == "mock"
    response = client.post(
        "/api/research",
        json={
            "session_id": "api",
            "query": "Research SPY fees and risks",
            "instrument_ids": ["SPY"],
        },
    )
    assert response.status_code == 200
    assert response.json()["evidence"]


def test_public_audit_requires_an_explicit_session() -> None:
    client = TestClient(app)
    assert client.get("/api/audit").status_code == 422
    assert client.get("/api/audit", params={"session_id": "browser-session"}).status_code == 200
