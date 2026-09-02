"""Domain models shared by policy, research, calculation and API layers."""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Intent(StrEnum):
    EDUCATION = "education"
    RESEARCH = "research"
    COMPARE = "compare"
    PORTFOLIO = "portfolio_analysis"
    ADVICE = "personalised_advice"
    EXECUTION = "trade_execution"


class PolicyOutcome(StrEnum):
    INFORMATIONAL = "informational"
    CLARIFICATION_REQUIRED = "clarification_required"
    EDUCATIONAL_ONLY = "educational_only"
    CAUTION = "caution"
    REFUSE = "refuse"
    HUMAN_REVIEW = "human_review"


class DataStatus(StrEnum):
    PUBLIC_PARAPHRASE = "public_source_paraphrase"
    SYNTHETIC = "synthetic_demo_data"


class UserProfile(BaseModel):
    """Voluntary research context, not a regulatory suitability assessment."""

    model_config = ConfigDict(extra="forbid")

    research_goal: str | None = None
    investment_horizon: str | None = None
    liquidity_need: str | None = None
    loss_tolerance: str | None = None
    investment_experience: str | None = None
    product_knowledge: str | None = None
    concentration_preference: str | None = None
    currency_exposure: str | None = None
    information_preference: str | None = None
    current_task: str | None = None
    missing_information: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    last_updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Instrument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    instrument_id: str
    symbol: str
    name: str
    instrument_type: str
    issuer: str
    currency: str
    region: str
    risk_level: int = Field(ge=1, le=5)
    complexity: str
    min_horizon_months: int = Field(ge=0)
    liquidity_days: int = Field(ge=0)
    expense_ratio: float = Field(ge=0.0)
    sectors: dict[str, float]
    regions: dict[str, float]
    data_status: DataStatus = DataStatus.SYNTHETIC
    as_of: date

    @field_validator("sectors", "regions")
    @classmethod
    def weights_sum_to_one(cls, value: dict[str, float]) -> dict[str, float]:
        if not value or any(weight < 0 for weight in value.values()):
            raise ValueError("exposure weights must be non-negative and non-empty")
        if abs(sum(value.values()) - 1.0) > 1e-6:
            raise ValueError("exposure weights must sum to one")
        return value


class ResearchDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_id: str
    instrument_id: str | None = None
    title: str
    document_type: str
    source_name: str
    source_url: str
    published_at: date
    retrieved_at: date
    content: str
    key_facts: list[str]
    structured_facts: dict[str, str] = Field(default_factory=dict)
    data_status: DataStatus
    checksum: str


class Evidence(BaseModel):
    document_id: str
    instrument_id: str | None = None
    title: str
    document_type: str
    source_name: str
    source_url: str
    published_at: date
    retrieved_at: date
    excerpt: str
    structured_facts: dict[str, str] = Field(default_factory=dict)
    score: float
    freshness: str
    data_status: DataStatus


class ClarificationCandidate(BaseModel):
    field: str
    question: str
    information_gain: float
    outcome_entropy: float
    answer_entropy: float
    possible_policy_outcomes: list[PolicyOutcome]
    reason: str


class ClarificationDecision(BaseModel):
    selected: ClarificationCandidate | None
    candidates: list[ClarificationCandidate]
    required_fields: list[str]
    missing_fields: list[str]


class PolicyHit(BaseModel):
    rule_id: str
    severity: str
    message: str


class PolicyDecision(BaseModel):
    outcome: PolicyOutcome
    hits: list[PolicyHit]
    rationale: str
    human_required: bool = False


class CalculationResult(BaseModel):
    metric: str
    value: float | dict[str, float] | None
    unit: str
    formula: str
    assumptions: list[str]
    data_status: DataStatus = DataStatus.SYNTHETIC


class CitedClaim(BaseModel):
    text: str
    citation_ids: list[str] = Field(default_factory=list)
    synthetic: bool = False


class EvidenceConflict(BaseModel):
    instrument_id: str
    fact_key: str
    values: dict[str, str]
    document_ids: list[str]


class ResearchRequest(BaseModel):
    session_id: str = "demo"
    query: str = Field(min_length=2, max_length=1500)
    profile: UserProfile | None = None
    instrument_ids: list[str] = Field(default_factory=list, max_length=5)


class ResearchResponse(BaseModel):
    session_id: str
    intent: Intent
    outcome: PolicyOutcome
    message: str
    disclaimer: str
    task_confidence: float
    profile: UserProfile
    clarification: ClarificationDecision | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    conflicts: list[EvidenceConflict] = Field(default_factory=list)
    calculations: list[CalculationResult] = Field(default_factory=list)
    claims: list[CitedClaim] = Field(default_factory=list)
    policy: PolicyDecision
    audit_id: str
    limitations: list[str] = Field(default_factory=list)


class CompareRequest(BaseModel):
    instrument_ids: list[str] = Field(min_length=2, max_length=4)


class CompareResponse(BaseModel):
    instruments: list[Instrument]
    metrics: dict[str, dict[str, CalculationResult]]
    comparability_notes: list[str]
    disclaimer: str


class Holding(BaseModel):
    instrument_id: str
    weight: float = Field(gt=0.0, le=1.0)


class PortfolioRequest(BaseModel):
    holdings: list[Holding] = Field(min_length=1, max_length=10)
    scenario_shock: float = Field(default=-0.15, ge=-1.0, le=1.0)

    @field_validator("holdings")
    @classmethod
    def portfolio_weights_sum_to_one(cls, holdings: list[Holding]) -> list[Holding]:
        if abs(sum(item.weight for item in holdings) - 1.0) > 1e-6:
            raise ValueError("portfolio weights must sum to one")
        return holdings


class PortfolioResponse(BaseModel):
    calculations: list[CalculationResult]
    sector_exposure: dict[str, float]
    region_exposure: dict[str, float]
    currency_exposure: dict[str, float]
    disclaimer: str


class AuditEvent(BaseModel):
    audit_id: str
    timestamp: datetime
    session_id: str
    query: str
    intent: Intent
    outcome: PolicyOutcome
    profile_changes: dict[str, dict[str, Any]]
    clarification: ClarificationDecision | None
    policy_hits: list[PolicyHit]
    evidence_ids: list[str]
    calculation_metrics: list[str]
    provider: str
    model: str
    prompt_version: str


class EvaluationMetric(BaseModel):
    name: str
    numerator: int
    denominator: int
    value: float
    definition: str


class BaselineResult(BaseModel):
    name: str
    passed: int
    cases: int
    value: float
    scope: str
    definition: str


class EvaluationReport(BaseModel):
    generated_at: datetime
    seed: int
    cases: int
    passed: int
    failed: int
    metrics: list[EvaluationMetric]
    baselines: list[BaselineResult]
    failures: list[dict[str, Any]]
