"""Expected-decision-information clarification planner.

Converge asks which product attribute would split the candidate posterior most. In finance there
is no hidden target product, so WealthGuard forward-simulates possible profile answers and asks
which missing field most changes the deterministic policy outcome. A small answer-entropy term
rewards useful profile resolution when policy outcomes tie.
"""

from __future__ import annotations

import math
from collections import Counter

from .models import (
    ClarificationCandidate,
    ClarificationDecision,
    Instrument,
    Intent,
    PolicyOutcome,
    UserProfile,
)
from .policy import evaluate, required_profile_fields

FIELD_OPTIONS: dict[str, list[tuple[str, float]]] = {
    "investment_horizon": [
        ("under_1_year", 0.20),
        ("1_to_3_years", 0.30),
        ("3_to_5_years", 0.25),
        ("over_5_years", 0.25),
    ],
    "liquidity_need": [("within_days", 0.35), ("within_months", 0.35), ("flexible", 0.30)],
    "loss_tolerance": [
        ("very_low", 0.15),
        ("low", 0.25),
        ("moderate", 0.35),
        ("high", 0.18),
        ("very_high", 0.07),
    ],
    "investment_experience": [
        ("none", 0.25),
        ("beginner", 0.35),
        ("intermediate", 0.30),
        ("advanced", 0.10),
    ],
    "product_knowledge": [("limited", 0.45), ("working", 0.40), ("advanced", 0.15)],
    "concentration_preference": [
        ("avoid_concentration", 0.55),
        ("neutral", 0.35),
        ("accept_concentration", 0.10),
    ],
    "currency_exposure": [
        ("home_currency_only", 0.35),
        ("limited_foreign", 0.45),
        ("accept_foreign", 0.20),
    ],
    "information_preference": [("plain_language", 0.55), ("balanced", 0.35), ("technical", 0.10)],
}


QUESTIONS = {
    "investment_horizon": "When might you need this money: within a year, 1–3 years, 3–5 years, or later?",
    "liquidity_need": "How quickly might you need access to the money: days, months, or is timing flexible?",
    "loss_tolerance": (
        "For this research, which loss range would make you stop and reassess: "
        "very low, low, moderate, high, or very high?"
    ),
    "investment_experience": (
        "How familiar are you with market-traded products: none, beginner, intermediate, or advanced?"
    ),
    "product_knowledge": "How well do you understand this product type: limited, working, or advanced knowledge?",
    "concentration_preference": (
        "Should the analysis flag concentrated positions aggressively, neutrally, or only at high levels?"
    ),
    "currency_exposure": "Should the analysis avoid, limit, or simply disclose foreign-currency exposure?",
    "information_preference": "Would you prefer a plain-language, balanced, or technical explanation?",
}


RELEVANCE: dict[Intent, dict[str, float]] = {
    Intent.ADVICE: {
        "investment_horizon": 1.20,
        "liquidity_need": 1.10,
        "loss_tolerance": 1.25,
        "investment_experience": 0.90,
        "product_knowledge": 0.85,
    },
    Intent.COMPARE: {"investment_horizon": 1.05, "liquidity_need": 1.00},
    Intent.PORTFOLIO: {
        "loss_tolerance": 1.15,
        "concentration_preference": 1.10,
        "currency_exposure": 1.05,
    },
}


def _entropy(probabilities: list[float]) -> float:
    return -sum(probability * math.log2(probability) for probability in probabilities if probability > 0)


def _outcome_entropy(outcomes: list[tuple[PolicyOutcome, float]]) -> float:
    totals: Counter[PolicyOutcome] = Counter()
    for outcome, probability in outcomes:
        totals[outcome] += probability
    return _entropy(list(totals.values()))


def plan(
    query: str,
    intent: Intent,
    profile: UserProfile,
    instruments: list[Instrument],
) -> ClarificationDecision:
    required = required_profile_fields(intent, instruments)
    missing = [field for field in required if not getattr(profile, field)]
    candidates: list[ClarificationCandidate] = []

    for field in missing:
        options = FIELD_OPTIONS[field]
        simulated: list[tuple[PolicyOutcome, float]] = []
        for value, probability in options:
            simulated_profile = profile.model_copy(update={field: value})
            decision = evaluate(
                query,
                intent,
                simulated_profile,
                instruments,
                include_missing=False,
            )
            simulated.append((decision.outcome, probability))
        answer_entropy = _entropy([probability for _, probability in options])
        outcome_entropy = _outcome_entropy(simulated)
        relevance = RELEVANCE.get(intent, {}).get(field, 0.75)
        information_gain = relevance * (outcome_entropy + 0.25 * answer_entropy)
        distinct = sorted(set(outcome for outcome, _ in simulated), key=lambda item: item.value)
        candidates.append(
            ClarificationCandidate(
                field=field,
                question=QUESTIONS[field],
                information_gain=round(information_gain, 6),
                outcome_entropy=round(outcome_entropy, 6),
                answer_entropy=round(answer_entropy, 6),
                possible_policy_outcomes=distinct,
                reason=(
                    f"Possible answers change {len(distinct)} policy path(s); the field has "
                    f"{answer_entropy:.2f} bits of unresolved profile information."
                ),
            )
        )

    candidates.sort(key=lambda item: (-item.information_gain, item.field))
    return ClarificationDecision(
        selected=candidates[0] if candidates else None,
        candidates=candidates,
        required_fields=required,
        missing_fields=missing,
    )
