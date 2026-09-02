"""Deterministic research-boundary and profile/product conflict policy."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Instrument, Intent, PolicyDecision, PolicyHit, PolicyOutcome, UserProfile


@dataclass(frozen=True)
class PatternRule:
    rule_id: str
    pattern: re.Pattern[str]
    outcome: PolicyOutcome
    severity: str
    message: str


def _pattern(value: str) -> re.Pattern[str]:
    return re.compile(value, re.IGNORECASE)


PATTERN_RULES = (
    PatternRule(
        "TRADE_EXECUTION",
        _pattern(r"\b(place|execute|submit)\b.{0,24}\b(order|trade)\b|替我买|帮我下单|执行交易"),
        PolicyOutcome.REFUSE,
        "critical",
        "The prototype cannot place, route or execute a trade.",
    ),
    PatternRule(
        "GUARANTEED_RETURN",
        _pattern(r"\b(guaranteed|risk[- ]?free|cannot lose|sure profit)\b|稳赚|保本保收益|绝不会亏|保证收益"),
        PolicyOutcome.REFUSE,
        "high",
        "Guaranteed or loss-free investment claims are not supported.",
    ),
    PatternRule(
        "POLICY_BYPASS",
        _pattern(r"ignore.{0,30}(policy|rules?|safety)|绕过.{0,12}(限制|规则)|忽略.{0,12}(政策|规则)"),
        PolicyOutcome.REFUSE,
        "critical",
        "Instructions to bypass product safeguards are rejected.",
    ),
    PatternRule(
        "SENSITIVE_DATA",
        _pattern(r"reveal.{0,24}(account|password|identity|private)|显示.{0,16}(账户|密码|身份证|隐私)"),
        PolicyOutcome.REFUSE,
        "critical",
        "The system does not expose account credentials or sensitive personal data.",
    ),
    PatternRule(
        "FINANCIAL_DISTRESS",
        _pattern(r"suicide|kill myself|borrow everything|gamble it all|自杀|不想活|借钱梭哈|赌博翻本"),
        PolicyOutcome.HUMAN_REVIEW,
        "critical",
        "Severe distress or gambling-related language requires a supportive human pathway, not product research.",
    ),
    PatternRule(
        "MINOR",
        _pattern(r"\b(i am|i'm) (1[0-7]|[0-9])\b|未成年|我今年(?:[0-9]|1[0-7])岁"),
        PolicyOutcome.EDUCATIONAL_ONLY,
        "high",
        "A minor-facing request is limited to general financial education.",
    ),
)


_HORIZON_MONTHS = {"under_1_year": 6, "1_to_3_years": 24, "3_to_5_years": 48, "over_5_years": 84}
_LOSS_LEVEL = {"very_low": 1, "low": 2, "moderate": 3, "high": 4, "very_high": 5}
_EXPERIENCE = {"none": 0, "beginner": 1, "intermediate": 2, "advanced": 3}


def required_profile_fields(intent: Intent, instruments: list[Instrument]) -> list[str]:
    if intent in {Intent.EDUCATION, Intent.RESEARCH, Intent.EXECUTION}:
        return []
    if intent == Intent.COMPARE:
        return ["investment_horizon", "liquidity_need"]
    if intent == Intent.PORTFOLIO:
        return ["loss_tolerance", "concentration_preference", "currency_exposure"]
    if intent == Intent.ADVICE:
        fields = ["investment_horizon", "liquidity_need", "loss_tolerance"]
        if any(instrument.complexity != "standard" or instrument.risk_level >= 5 for instrument in instruments):
            fields.extend(["investment_experience", "product_knowledge"])
        return fields
    return []


def _profile_hits(profile: UserProfile, instruments: list[Instrument]) -> list[PolicyHit]:
    hits: list[PolicyHit] = []
    horizon = _HORIZON_MONTHS.get(profile.investment_horizon or "")
    tolerance = _LOSS_LEVEL.get(profile.loss_tolerance or "")
    experience = _EXPERIENCE.get(profile.investment_experience or "")
    high_liquidity = profile.liquidity_need == "within_days"

    for instrument in instruments:
        if horizon is not None and horizon < instrument.min_horizon_months:
            hits.append(
                PolicyHit(
                    rule_id="HORIZON_CONFLICT",
                    severity="high",
                    message=f"{instrument.symbol}'s illustrative minimum horizon exceeds the stated research horizon.",
                )
            )
        if high_liquidity and instrument.liquidity_days > 1:
            hits.append(
                PolicyHit(
                    rule_id="LIQUIDITY_CONFLICT",
                    severity="high",
                    message=f"{instrument.symbol}'s synthetic liquidity assumption conflicts with access within days.",
                )
            )
        if tolerance is not None and instrument.risk_level > tolerance + 1:
            hits.append(
                PolicyHit(
                    rule_id="LOSS_TOLERANCE_CONFLICT",
                    severity="high",
                    message=f"{instrument.symbol}'s risk level materially exceeds the stated loss-tolerance band.",
                )
            )
        if instrument.complexity != "standard" and (experience or 0) < 2:
            hits.append(
                PolicyHit(
                    rule_id="COMPLEXITY_KNOWLEDGE_GAP",
                    severity="high",
                    message=f"{instrument.symbol} is modelled as complex and requires additional education or review.",
                )
            )
    return hits


def evaluate(
    query: str,
    intent: Intent,
    profile: UserProfile,
    instruments: list[Instrument],
    *,
    include_missing: bool = True,
) -> PolicyDecision:
    hits: list[PolicyHit] = []
    terminal: PolicyOutcome | None = None
    for rule in PATTERN_RULES:
        if rule.pattern.search(query):
            hits.append(PolicyHit(rule_id=rule.rule_id, severity=rule.severity, message=rule.message))
            if rule.outcome in {PolicyOutcome.REFUSE, PolicyOutcome.HUMAN_REVIEW}:
                terminal = rule.outcome
                break
            terminal = terminal or rule.outcome

    if terminal in {PolicyOutcome.REFUSE, PolicyOutcome.HUMAN_REVIEW}:
        return PolicyDecision(
            outcome=terminal,
            hits=hits,
            rationale=hits[-1].message,
            human_required=terminal == PolicyOutcome.HUMAN_REVIEW,
        )

    required = required_profile_fields(intent, instruments)
    missing = [field for field in required if not getattr(profile, field)]
    if include_missing and missing:
        hits.append(
            PolicyHit(
                rule_id="MISSING_RESEARCH_CONTEXT",
                severity="medium",
                message="Additional context could materially change the safe research framing: " + ", ".join(missing),
            )
        )
        return PolicyDecision(
            outcome=PolicyOutcome.CLARIFICATION_REQUIRED,
            hits=hits,
            rationale="A high-value clarification is required before personalised framing.",
        )

    profile_hits = _profile_hits(profile, instruments)
    hits.extend(profile_hits)
    if profile_hits:
        return PolicyDecision(
            outcome=PolicyOutcome.CAUTION,
            hits=hits,
            rationale="The supplied research context conflicts with one or more product characteristics.",
        )

    if terminal == PolicyOutcome.EDUCATIONAL_ONLY or intent == Intent.ADVICE:
        if intent == Intent.ADVICE:
            hits.append(
                PolicyHit(
                    rule_id="ADVICE_REFRAME",
                    severity="medium",
                    message="The request is reframed from a personal recommendation to evidence-based research.",
                )
            )
        return PolicyDecision(
            outcome=PolicyOutcome.EDUCATIONAL_ONLY,
            hits=hits,
            rationale="The system can provide education and sourced research, not personalised investment advice.",
        )

    return PolicyDecision(
        outcome=PolicyOutcome.INFORMATIONAL,
        hits=hits,
        rationale="The request is within the educational research boundary.",
    )
