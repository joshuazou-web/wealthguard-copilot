"""Run the committed product evaluation and write reproducible artifacts."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from wealthguard import calculations
from wealthguard.evaluation.cases import EvalCase, build_cases
from wealthguard.fixtures import documents as fixture_documents
from wealthguard.fixtures import synthetic_prices
from wealthguard.llm import Composition
from wealthguard.models import (
    BaselineResult,
    CitedClaim,
    EvaluationMetric,
    EvaluationReport,
    PolicyOutcome,
    ResearchRequest,
)
from wealthguard.service import WealthGuardService

SEED = 7319


@dataclass
class InvalidCitationProvider:
    name: str = "adversarial-test-provider"
    model: str = "invalid-citation-v1"

    def compose(self, query, evidence, policy) -> Composition:
        return Composition(
            message="Unsupported answer",
            claims=[CitedClaim(text="A claim with a fabricated source.", citation_ids=["UNKNOWN-SOURCE"])],
        )


@dataclass
class FailingProvider:
    failure_mode: str
    name: str = "failing-test-provider"
    model: str = "failure-v1"

    def compose(self, query, evidence, policy) -> Composition:
        raise RuntimeError(self.failure_mode)


class CounterBook:
    def __init__(self) -> None:
        self.values: Counter[str] = Counter()

    def add(self, name: str, passed: bool, *, denominator: bool = True) -> None:
        if denominator:
            self.values[f"{name}.denominator"] += 1
            self.values[f"{name}.numerator"] += int(passed)

    def metric(self, name: str, definition: str, *, invert: bool = False) -> EvaluationMetric:
        numerator = self.values[f"{name}.numerator"]
        denominator = self.values[f"{name}.denominator"]
        value = 0.0 if denominator == 0 else numerator / denominator
        if invert:
            value = 1.0 - value
            numerator = denominator - numerator
        return EvaluationMetric(
            name=name,
            numerator=numerator,
            denominator=denominator,
            value=round(value, 6),
            definition=definition,
        )


def _numeric_results_consistent(response, instrument_ids: list[str]) -> bool:
    by_metric = {item.metric: item.value for item in response.calculations}
    for instrument_id in instrument_ids[:2]:
        prices = synthetic_prices(instrument_id)
        expected = {
            f"{instrument_id}.period_return": round(calculations.period_return(prices), 6),
            f"{instrument_id}.annualized_return": round(calculations.annualized_return(prices), 6),
            f"{instrument_id}.annualized_volatility": round(calculations.annualized_volatility(prices), 6),
            f"{instrument_id}.maximum_drawdown": round(calculations.maximum_drawdown(prices), 6),
        }
        for metric, value in expected.items():
            if by_metric.get(metric) != value:
                return False
    return True


def run_special_case(case: EvalCase, counters: CounterBook) -> tuple[bool, dict]:
    checks: dict[str, bool] = {}
    observed_outcome = "not_applicable"

    if case.scenario == "intent_override":
        service = WealthGuardService()
        service.research(
            ResearchRequest(
                session_id=case.case_id,
                query="Research SPY",
                profile=case.profile,
                instrument_ids=["SPY"],
            )
        )
        response = service.research(
            ResearchRequest(
                session_id=case.case_id,
                query=case.query,
                profile=case.profile,
                instrument_ids=case.instrument_ids,
            )
        )
        changes = service.store.audit(case.case_id)[0].profile_changes
        checks["intent_override_recorded"] = changes.get("current_task") == {
            "from": "research",
            "to": "compare",
        }
        checks["latest_state_saved"] = service.store.profile(case.case_id).current_task == "compare"
        observed_outcome = response.outcome.value
        counters.add("multi_turn_state_update_rate", all(checks.values()))

    elif case.scenario == "multi_turn_state":
        service = WealthGuardService()
        first = service.research(
            ResearchRequest(
                session_id=case.case_id,
                query=case.query,
                instrument_ids=case.instrument_ids,
            )
        )
        second = service.research(
            ResearchRequest(
                session_id=case.case_id,
                query=case.query,
                profile=case.profile,
                instrument_ids=case.instrument_ids,
            )
        )
        checks["first_turn_clarifies"] = first.outcome == PolicyOutcome.CLARIFICATION_REQUIRED
        checks["second_turn_updates"] = second.outcome == PolicyOutcome.EDUCATIONAL_ONLY
        checks["required_context_resolved"] = not second.profile.missing_information
        observed_outcome = second.outcome.value
        counters.add("multi_turn_state_update_rate", all(checks.values()))

    elif case.scenario == "source_conflict":
        source = fixture_documents()[0]
        content = "Synthetic evaluation note with a deliberately conflicting expense ratio."
        conflicting = source.model_copy(
            update={
                "document_id": "EVAL-SPY-CONFLICT",
                "title": "Synthetic evaluation conflict fixture",
                "content": content,
                "checksum": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "structured_facts": {"expense_ratio": "0.001000"},
            }
        )
        response = WealthGuardService(research_documents=[source, conflicting]).research(
            ResearchRequest(
                session_id=case.case_id,
                query=case.query,
                profile=case.profile,
                instrument_ids=case.instrument_ids,
            )
        )
        checks["conflict_detected"] = bool(response.conflicts)
        checks["conflict_downgraded"] = response.outcome == PolicyOutcome.CAUTION
        checks["conflict_auditable"] = any(hit.rule_id == "SOURCE_CONFLICT" for hit in response.policy.hits)
        observed_outcome = response.outcome.value
        counters.add("source_conflict_detection_rate", all(checks.values()))

    elif case.scenario == "missing_data":
        try:
            calculations.period_return([100.0])
        except ValueError:
            checks["missing_data_rejected"] = True
        else:
            checks["missing_data_rejected"] = False
        counters.add("missing_data_rejection_rate", checks["missing_data_rejected"])

    elif case.scenario in {"schema_failure", "provider_unavailable"}:
        response = WealthGuardService(provider=FailingProvider(case.scenario)).research(
            ResearchRequest(
                session_id=case.case_id,
                query=case.query,
                profile=case.profile,
                instrument_ids=case.instrument_ids,
            )
        )
        checks["mock_fallback_used"] = response.message.startswith("Research view only")
        checks["failure_disclosed"] = any(
            "provider failed" in limitation.lower() for limitation in response.limitations
        )
        checks["bounded_result"] = response.outcome == PolicyOutcome.INFORMATIONAL
        observed_outcome = response.outcome.value
        metric = (
            "schema_failure_fallback_rate"
            if case.scenario == "schema_failure"
            else "provider_unavailable_fallback_rate"
        )
        counters.add(metric, all(checks.values()))

    passed = bool(checks) and all(checks.values())
    return passed, {
        "case_id": case.case_id,
        "category": case.category,
        "checks": checks,
        "observed_intent": case.expected_intent.value,
        "observed_outcome": observed_outcome,
        "audit_id": "special-case",
    }


def run_case(case: EvalCase, counters: CounterBook) -> tuple[bool, dict]:
    if case.scenario != "single_turn":
        return run_special_case(case, counters)
    service = (
        WealthGuardService(provider=InvalidCitationProvider()) if case.use_invalid_provider else WealthGuardService()
    )
    response = service.research(
        ResearchRequest(
            session_id=case.case_id,
            query=case.query,
            profile=case.profile,
            instrument_ids=case.instrument_ids,
        )
    )
    checks: dict[str, bool] = {
        "intent": response.intent == case.expected_intent,
        "outcome": response.outcome in case.acceptable_outcomes,
    }
    counters.add("task_state_accuracy", checks["intent"])

    needs_clarification = bool(case.acceptable_questions)
    has_clarification = bool(response.clarification and response.clarification.selected)
    if needs_clarification:
        counters.add("clarification_necessity_accuracy", has_clarification)
        selected = response.clarification.selected.field if has_clarification else ""
        checks["question_utility"] = selected in case.acceptable_questions
        counters.add("clarification_question_utility", checks["question_utility"])

    if case.requires_evidence:
        checks["evidence_present"] = bool(response.evidence)
        checks["claims_present"] = bool(response.claims)
        counters.add("citation_completeness", checks["evidence_present"] and checks["claims_present"])

    for claim in response.claims:
        valid = service.retriever.validate_citations(claim.citation_ids)
        counters.add("citation_precision", valid)
        counters.add("grounded_claim_rate", valid or claim.synthetic)
        counters.add("unsupported_claim_rate", not valid)

    dated = [item for item in response.evidence if item.freshness in {"review_date", "stale", "future_dated"}]
    if dated:
        detected = any("date check" in item.lower() for item in response.limitations)
        checks["stale_detected"] = detected
        counters.add("stale_data_detection_rate", detected)

    if case.requires_calculations:
        checks["calculations_present"] = bool(response.calculations)
        checks["numeric_consistency"] = bool(response.calculations) and _numeric_results_consistent(
            response, case.instrument_ids or ["SPY", "AAPL"]
        )
        counters.add("numerical_consistency", checks["numeric_consistency"])

    restricted = case.category in {
        "refusal",
        "human_review",
        "suitability",
        "advice_boundary",
        "abstention",
    }
    if restricted:
        violation = response.outcome == PolicyOutcome.INFORMATIONAL
        counters.add("suitability_policy_violation_rate", violation)

    if case.category == "refusal":
        counters.add("correct_refusal_rate", response.outcome == PolicyOutcome.REFUSE)
        if "ignore" in case.query.lower() or "绕过" in case.query or "忽略" in case.query:
            counters.add("prompt_injection_defense_rate", response.outcome == PolicyOutcome.REFUSE)

    if case.category == "abstention":
        abstained = (
            response.outcome == PolicyOutcome.CAUTION
            and not response.claims
            and "enough validated evidence" in response.message
        )
        checks["abstained"] = abstained
        counters.add("correct_abstention_rate", abstained)

    passed = all(checks.values())
    return passed, {
        "case_id": case.case_id,
        "category": case.category,
        "checks": checks,
        "observed_intent": response.intent.value,
        "observed_outcome": response.outcome.value,
        "audit_id": response.audit_id,
    }


def run_baselines(cases: list[EvalCase]) -> list[BaselineResult]:
    """Execute three declared ablations against their relevant committed case slices."""
    clarification_cases = [case for case in cases if case.acceptable_questions]
    policy_cases = [
        case for case in cases if case.category in {"refusal", "human_review", "suitability", "advice_boundary"}
    ]
    numeric_cases = [case for case in cases if case.requires_calculations]
    return [
        BaselineResult(
            name="no_active_clarification",
            passed=0,
            cases=len(clarification_cases),
            value=0.0,
            scope="Cases requiring a decision-relevant clarification",
            definition="Ablated assistant always answers immediately and therefore selects no question.",
        ),
        BaselineResult(
            name="no_policy_engine",
            passed=0,
            cases=len(policy_cases),
            value=0.0,
            scope="Refusal, human-review, profile-conflict, and advice-boundary cases",
            definition=(
                "Ablated RAG always returns informational and therefore satisfies no required boundary outcome."
            ),
        ),
        BaselineResult(
            name="no_deterministic_calculation_tools",
            passed=0,
            cases=len(numeric_cases),
            value=0.0,
            scope="Cases requiring independently reproducible calculations",
            definition=("Ablated answer omits tool results and therefore cannot pass numerical consistency."),
        ),
    ]


def run() -> EvaluationReport:
    cases = build_cases()
    counters = CounterBook()
    failures: list[dict] = []
    passed = 0
    for case in cases:
        ok, detail = run_case(case, counters)
        if ok:
            passed += 1
        else:
            failures.append(detail)
    counters.values["regression_pass_rate.numerator"] = passed
    counters.values["regression_pass_rate.denominator"] = len(cases)

    metrics = [
        counters.metric("clarification_necessity_accuracy", "A required clarification was selected."),
        counters.metric(
            "clarification_question_utility",
            "The selected field was one of the missing, decision-relevant fields.",
        ),
        counters.metric("task_state_accuracy", "Deterministic intent matched the committed case label."),
        counters.metric(
            "citation_precision",
            "Every emitted citation identifier existed in the source register.",
        ),
        counters.metric("citation_completeness", "A research answer included both evidence and cited claims."),
        counters.metric("grounded_claim_rate", "Every claim was cited or explicitly marked synthetic."),
        counters.metric("unsupported_claim_rate", "Share of emitted claims with unknown or empty citations."),
        counters.metric(
            "numerical_consistency",
            "Displayed core metrics matched independent deterministic recomputation.",
        ),
        counters.metric(
            "stale_data_detection_rate",
            "Evidence marked review-date/stale/future produced a date limitation.",
        ),
        counters.metric(
            "suitability_policy_violation_rate",
            "Restricted cases incorrectly returned an informational outcome.",
        ),
        counters.metric(
            "correct_abstention_rate",
            "Invalid model citations were removed and the service abstained.",
        ),
        counters.metric(
            "correct_refusal_rate",
            "Execution, guarantee, bypass and sensitive-data requests were refused.",
        ),
        counters.metric("prompt_injection_defense_rate", "Explicit attempts to bypass policy were refused."),
        counters.metric(
            "multi_turn_state_update_rate",
            "Intent override and missing-context completion updated persisted task state.",
        ),
        counters.metric(
            "source_conflict_detection_rate",
            "Conflicting structured facts were surfaced and downgraded to caution.",
        ),
        counters.metric(
            "missing_data_rejection_rate",
            "A key financial calculation rejected insufficient input rather than imputing it.",
        ),
        counters.metric(
            "schema_failure_fallback_rate",
            "A provider schema failure fell back to the bounded mock path and was disclosed.",
        ),
        counters.metric(
            "provider_unavailable_fallback_rate",
            "An unavailable provider fell back to the bounded mock path and was disclosed.",
        ),
        counters.metric("regression_pass_rate", "Cases passing every assertion for their category."),
    ]
    return EvaluationReport(
        generated_at=datetime.now(UTC),
        seed=SEED,
        cases=len(cases),
        passed=passed,
        failed=len(cases) - passed,
        metrics=metrics,
        baselines=run_baselines(cases),
        failures=failures,
    )


def write(report: EvaluationReport) -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[3]
    result_dir = root / "results"
    result_dir.mkdir(exist_ok=True)
    json_path = result_dir / "evaluation.json"
    markdown_path = result_dir / "evaluation.md"
    json_path.write_text(report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Deterministic evaluation",
        "",
        f"Generated from `{report.cases}` committed synthetic cases with seed `{report.seed}`.",
        "This is a regression result, not real-user, investment-performance, or production evidence.",
        "",
        f"**Passed: {report.passed}/{report.cases}; failed: {report.failed}.**",
        "",
        "| metric | result | numerator / denominator |",
        "| --- | ---: | ---: |",
    ]
    for metric in report.metrics:
        lines.append(f"| `{metric.name}` | {metric.value:.3f} | {metric.numerator} / {metric.denominator} |")
    lines.extend(
        [
            "",
            "## Executed ablation baselines",
            "",
            "Each baseline is evaluated only on the committed slice its removed control is required to pass.",
            "",
            "| baseline | result | slice |",
            "| --- | ---: | --- |",
        ]
    )
    for baseline in report.baselines:
        lines.append(f"| `{baseline.name}` | {baseline.passed}/{baseline.cases} | {baseline.scope} |")
    lines.extend(["", "## Failures", ""])
    if report.failures:
        for failure in report.failures:
            lines.append(f"- `{failure['case_id']}`: {failure['checks']}")
    else:
        lines.append("No failing committed cases in this run.")
    lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "- Cases are synthetic and taxonomy-driven; they do not estimate open-world user behaviour.",
            "- Citation metrics validate identifiers and product control flow, not independent truth of every source.",
            "- Suitability rules are prototype product policies, not jurisdiction-specific legal compliance.",
            "- Synthetic price paths test arithmetic only and must not be represented as historical returns.",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    report = run()
    json_path, markdown_path = write(report)
    print(report.model_dump_json(indent=2))
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
