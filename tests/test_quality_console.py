from fastapi.testclient import TestClient
from wealthguard.api import app
from wealthguard.quality import BAD_CASES, ERROR_DEFINITIONS, ErrorType, filter_bad_cases


def test_taxonomy_covers_required_error_types() -> None:
    assert {item.error_type for item in ERROR_DEFINITIONS} == set(ErrorType)
    assert all(item.recommended_fix and item.responsibility_layer for item in ERROR_DEFINITIONS)


def test_bad_cases_are_anonymised_and_filterable() -> None:
    cases = filter_bad_cases(scenario="announcement", severity="high")
    assert cases
    assert all(item.scenario == "announcement" and item.severity == "high" for item in cases)
    serialised = " ".join(item.model_dump_json() for item in BAD_CASES).lower()
    assert "api_key" not in serialised
    assert "account_number" not in serialised
    assert all(item.data_status == "synthetic_evaluation_case" for item in BAD_CASES)


def test_quality_api_filters_cases() -> None:
    response = TestClient(app).get(
        "/api/quality/cases",
        params={"error_type": "ADVICE_BOUNDARY"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["case_id"] == "WG-QA-06"
