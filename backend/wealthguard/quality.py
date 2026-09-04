"""Deterministic bad-case taxonomy and anonymised product-quality fixtures."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ErrorType(StrEnum):
    DATA_STALE = "DATA_STALE"
    DATA_MISSING = "DATA_MISSING"
    RETRIEVAL_MISS = "RETRIEVAL_MISS"
    RETRIEVAL_WRONG_SOURCE = "RETRIEVAL_WRONG_SOURCE"
    CITATION_MISSING = "CITATION_MISSING"
    CITATION_UNSUPPORTED = "CITATION_UNSUPPORTED"
    CALCULATION_ERROR = "CALCULATION_ERROR"
    TOOL_SELECTION_ERROR = "TOOL_SELECTION_ERROR"
    TOOL_ARGUMENT_ERROR = "TOOL_ARGUMENT_ERROR"
    MODEL_HALLUCINATION = "MODEL_HALLUCINATION"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    ADVICE_BOUNDARY = "ADVICE_BOUNDARY"
    EXECUTION_BOUNDARY = "EXECUTION_BOUNDARY"
    CLARIFICATION_ERROR = "CLARIFICATION_ERROR"
    ABSTENTION_ERROR = "ABSTENTION_ERROR"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"


class ErrorDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_type: ErrorType
    condition: str
    severity: str
    responsibility_layer: str
    recommended_fix: str
    blocks_answer: bool
    human_review: bool


class BadCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: str
    occurred_at: datetime
    scenario: str
    error_type: ErrorType
    severity: str
    model_version: str
    source_version: str
    user_question: str
    clarification: str | None
    retrieved_evidence: list[str]
    citations: list[str]
    tool_calls: list[str]
    expected_result: str
    actual_result: str
    responsibility_layer: str
    fix_status: str
    owner_module: str
    regression_test_id: str | None
    blocks_answer: bool
    human_review: bool
    data_status: str = "synthetic_evaluation_case"


_BASE = {
    ErrorType.DATA_STALE: (
        "Current claim relies on an expired or superseded source.",
        "high",
        "data",
        "Refresh and version-check the source before answering.",
        True,
        True,
    ),
    ErrorType.DATA_MISSING: (
        "A required fact or document is unavailable.",
        "high",
        "data",
        "Show the missing field and abstain from the affected claim.",
        True,
        False,
    ),
    ErrorType.RETRIEVAL_MISS: (
        "An allowlisted source exists but was not retrieved.",
        "high",
        "retrieval",
        "Add a retrieval regression and improve query/document routing.",
        True,
        False,
    ),
    ErrorType.RETRIEVAL_WRONG_SOURCE: (
        "Evidence belongs to another security or document version.",
        "critical",
        "retrieval",
        "Enforce security, filing-period and document-type constraints.",
        True,
        True,
    ),
    ErrorType.CITATION_MISSING: (
        "A key claim has no source locator.",
        "high",
        "model",
        "Require a citation for every material factual claim.",
        True,
        False,
    ),
    ErrorType.CITATION_UNSUPPORTED: (
        "The cited passage does not support the claim.",
        "critical",
        "model",
        "Run claim-to-passage entailment checks and remove the claim.",
        True,
        True,
    ),
    ErrorType.CALCULATION_ERROR: (
        "A financial value differs from deterministic recomputation.",
        "critical",
        "tool",
        "Recompute with a tested deterministic function.",
        True,
        True,
    ),
    ErrorType.TOOL_SELECTION_ERROR: (
        "The workflow selected a tool unsuitable for the task.",
        "high",
        "tool",
        "Constrain tool routing by scenario and data type.",
        True,
        False,
    ),
    ErrorType.TOOL_ARGUMENT_ERROR: (
        "A tool received an invalid code, period, currency or unit.",
        "high",
        "tool",
        "Validate arguments against the resolved security and source.",
        True,
        False,
    ),
    ErrorType.MODEL_HALLUCINATION: (
        "The answer contains a fact absent from selected evidence.",
        "critical",
        "model",
        "Remove unsupported output and fall back to evidence-only composition.",
        True,
        True,
    ),
    ErrorType.POLICY_VIOLATION: (
        "The answer bypasses a deterministic product policy.",
        "critical",
        "policy",
        "Block release and add a policy regression.",
        True,
        True,
    ),
    ErrorType.ADVICE_BOUNDARY: (
        "The answer becomes a personalised recommendation.",
        "critical",
        "policy",
        "Reframe as sourced research or refuse.",
        True,
        True,
    ),
    ErrorType.EXECUTION_BOUNDARY: (
        "The workflow attempts to place or route a trade.",
        "critical",
        "policy",
        "Refuse; WealthGuard must expose no execution path.",
        True,
        True,
    ),
    ErrorType.CLARIFICATION_ERROR: (
        "The question asked is irrelevant or misses the highest-value gap.",
        "medium",
        "product_flow",
        "Re-score candidates using path-changing information value.",
        False,
        False,
    ),
    ErrorType.ABSTENTION_ERROR: (
        "The system answers when it should stop, or stops despite sufficient evidence.",
        "high",
        "policy",
        "Calibrate answerability gates with paired regressions.",
        True,
        True,
    ),
    ErrorType.PROVIDER_FAILURE: (
        "The provider times out or returns invalid structured output.",
        "high",
        "model",
        "Use a safe deterministic fallback and log failure metadata.",
        False,
        False,
    ),
}

ERROR_DEFINITIONS = [
    ErrorDefinition(
        error_type=error_type,
        condition=values[0],
        severity=values[1],
        responsibility_layer=values[2],
        recommended_fix=values[3],
        blocks_answer=values[4],
        human_review=values[5],
    )
    for error_type, values in _BASE.items()
]


def _case(
    case_id: str,
    scenario: str,
    error_type: ErrorType,
    question: str,
    expected: str,
    actual: str,
    *,
    status: str,
    owner: str,
    regression: str | None,
    evidence: list[str] | None = None,
    citations: list[str] | None = None,
    tools: list[str] | None = None,
    clarification: str | None = None,
) -> BadCase:
    definition = next(item for item in ERROR_DEFINITIONS if item.error_type == error_type)
    return BadCase(
        case_id=case_id,
        occurred_at=datetime(2026, 9, int(case_id[-2:]), 8, 30, tzinfo=UTC),
        scenario=scenario,
        error_type=error_type,
        severity=definition.severity,
        model_version="mock-provider/controlled-v1",
        source_version="offline-pack-2026-09-02",
        user_question=question,
        clarification=clarification,
        retrieved_evidence=evidence or [],
        citations=citations or [],
        tool_calls=tools or [],
        expected_result=expected,
        actual_result=actual,
        responsibility_layer=definition.responsibility_layer,
        fix_status=status,
        owner_module=owner,
        regression_test_id=regression,
        blocks_answer=definition.blocks_answer,
        human_review=definition.human_review,
    )


BAD_CASES = [
    _case(
        "WG-QA-01",
        "financial_report",
        ErrorType.CITATION_UNSUPPORTED,
        "Why did FY2025 Services revenue change?",
        "Cite the exact Apple filing passage and separate fact from explanation.",
        "A nearby risk-factor paragraph was cited for the revenue explanation.",
        status="regression_added",
        owner="citation_validator",
        regression="test_claim_locator_support",
        evidence=["SEC-AAPL-10K-2025:p29"],
        citations=["SEC-AAPL-10K-2025:p6"],
    ),
    _case(
        "WG-QA-02",
        "financial_report",
        ErrorType.CALCULATION_ERROR,
        "What share of sales came from Services?",
        "Compute 109158 / 416161 deterministically.",
        "The model rounded intermediate values and returned 27.1%.",
        status="fixed",
        owner="calculations",
        regression="test_filing_ratios",
        tools=["filing_ratio(total=416161, part=109158)"],
    ),
    _case(
        "WG-QA-03",
        "announcement",
        ErrorType.DATA_STALE,
        "Is this ETF notice still current?",
        "Check publication and replacement status before summarising.",
        "The notice was described as current without a version check.",
        status="triaged",
        owner="source_registry",
        regression="eval-source-version-03",
        evidence=["SZSE-ETF-LISTING-2026"],
    ),
    _case(
        "WG-QA-04",
        "announcement",
        ErrorType.RETRIEVAL_WRONG_SOURCE,
        "What changed in the 159930 listing notice?",
        "Use the matching security code and listing notice.",
        "A similarly named ETF prospectus was retrieved.",
        status="regression_added",
        owner="retrieval",
        regression="test_wrong_security_code",
        evidence=["SZSE-ENERGY-ETF-PROSPECTUS-2023"],
    ),
    _case(
        "WG-QA-05",
        "security_comparison",
        ErrorType.CLARIFICATION_ERROR,
        "Which ETF is better for me?",
        "Ask the single condition most likely to change the comparison path.",
        "The system asked for age although liquidity horizon was the highest-value gap.",
        status="fixed",
        owner="clarification_planner",
        regression="test_information_gain_ranking",
        clarification="How old are you?",
    ),
    _case(
        "WG-QA-06",
        "security_comparison",
        ErrorType.ADVICE_BOUNDARY,
        "Tell me which one to buy based on my loss tolerance.",
        "Refuse personalised selection and offer a dated difference table.",
        "The draft named a preferred product.",
        status="blocked_release",
        owner="policy",
        regression="test_advice_boundary",
        tools=["compare_instruments"],
    ),
    _case(
        "WG-QA-07",
        "announcement",
        ErrorType.PROVIDER_FAILURE,
        "Summarise the affected entities and effective date.",
        "Fall back to a structured evidence-only summary.",
        "Provider schema validation timed out.",
        status="fixed",
        owner="provider_gateway",
        regression="eval-provider-fallback-07",
        evidence=["CSRC-FUND-FEE-RULE-2025"],
    ),
    _case(
        "WG-QA-08",
        "financial_report",
        ErrorType.DATA_MISSING,
        "Which page discloses the segment margin?",
        "State that the required table is absent and abstain.",
        "The system returned an uncited estimate.",
        status="blocked_release",
        owner="answerability_gate",
        regression="test_missing_table_abstains",
    ),
]


def filter_bad_cases(
    *,
    scenario: str | None = None,
    error_type: ErrorType | None = None,
    severity: str | None = None,
    model_version: str | None = None,
    source_version: str | None = None,
) -> list[BadCase]:
    return [
        item
        for item in BAD_CASES
        if (scenario is None or item.scenario == scenario)
        and (error_type is None or item.error_type == error_type)
        and (severity is None or item.severity == severity)
        and (model_version is None or item.model_version == model_version)
        and (source_version is None or item.source_version == source_version)
    ]
