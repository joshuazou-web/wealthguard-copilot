"""Application service that orchestrates state, policy, evidence, tools and audit."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from . import calculations, clarification, intent
from . import evidence as evidence_checks
from .fixtures import INSTRUMENTS, instrument_map, synthetic_prices
from .fixtures import documents as fixture_documents
from .ingestion import ingest_documents
from .llm import PROMPT_VERSION, MockProvider, Provider, provider_from_environment
from .models import (
    AuditEvent,
    CalculationResult,
    CompareRequest,
    CompareResponse,
    DataStatus,
    Instrument,
    PolicyDecision,
    PolicyHit,
    PolicyOutcome,
    PortfolioRequest,
    PortfolioResponse,
    ResearchDocument,
    ResearchRequest,
    ResearchResponse,
    UserProfile,
)
from .policy import evaluate, required_profile_fields
from .retrieval import Retriever
from .store import SessionStore

DISCLAIMER = "For educational and research purposes only. Not investment advice."


class WealthGuardService:
    def __init__(
        self,
        provider: Provider | None = None,
        research_documents: list[ResearchDocument] | None = None,
    ) -> None:
        self.instruments = instrument_map()
        self.documents = ingest_documents(research_documents or fixture_documents())
        self.retriever = Retriever(self.documents)
        self.provider = provider or provider_from_environment()
        self.store = SessionStore()

    def list_instruments(self) -> list[Instrument]:
        return list(INSTRUMENTS)

    def _select_instruments(self, query: str, requested: list[str]) -> list[Instrument]:
        identifiers = [value.upper() for value in requested if value.upper() in self.instruments]
        query_upper = query.upper()
        for instrument_id, instrument in self.instruments.items():
            if instrument_id in query_upper or instrument.symbol.upper() in query_upper:
                identifiers.append(instrument_id)
        identifiers = list(dict.fromkeys(identifiers))
        if not identifiers:
            identifiers = ["SPY", "AAPL", "WGBOND", "WGCASH"]
        return [self.instruments[identifier] for identifier in identifiers[:4]]

    def _profile_confidence(self, profile: UserProfile, required: list[str]) -> float:
        if not required:
            return 1.0
        complete = sum(bool(getattr(profile, field)) for field in required)
        return round(complete / len(required), 4)

    def _calculation_results(self, instruments: list[Instrument]) -> list[CalculationResult]:
        results: list[CalculationResult] = []
        for instrument in instruments[:2]:
            prices = synthetic_prices(instrument.instrument_id)
            assumptions = [
                "Illustrative monthly price series generated with a fixed seed.",
                "The result is not the instrument's historical or forecast performance.",
                "Twelve periods per year are assumed.",
            ]
            prefix = instrument.symbol
            results.extend(
                [
                    CalculationResult(
                        metric=f"{prefix}.period_return",
                        value=round(calculations.period_return(prices), 6),
                        unit="decimal return",
                        formula="last_price / first_price - 1",
                        assumptions=assumptions,
                    ),
                    CalculationResult(
                        metric=f"{prefix}.annualized_return",
                        value=round(calculations.annualized_return(prices), 6),
                        unit="decimal per year",
                        formula="(last_price / first_price) ** (12 / periods) - 1",
                        assumptions=assumptions,
                    ),
                    CalculationResult(
                        metric=f"{prefix}.annualized_volatility",
                        value=round(calculations.annualized_volatility(prices), 6),
                        unit="decimal per year",
                        formula="sample_stdev(periodic_returns) * sqrt(12)",
                        assumptions=assumptions,
                    ),
                    CalculationResult(
                        metric=f"{prefix}.maximum_drawdown",
                        value=round(calculations.maximum_drawdown(prices), 6),
                        unit="decimal drawdown",
                        formula="min(price / running_peak - 1)",
                        assumptions=assumptions,
                    ),
                    CalculationResult(
                        metric=f"{prefix}.fee_impact",
                        value=calculations.fee_impact(10_000, 0.05, instrument.expense_ratio, 10),
                        unit="currency units after 10 years",
                        formula="principal * (1 + gross_return - annual_fee) ** years",
                        assumptions=[
                            "Illustrative principal 10,000 and constant gross annual return 5%.",
                            "No taxes, transaction costs, cash flows or changing fee schedules.",
                        ],
                    ),
                ]
            )
        if any(instrument.instrument_id == "AAPL" for instrument in instruments):
            ratios = calculations.selected_financial_ratios(416_161, 391_035, 109_158)
            results.append(
                CalculationResult(
                    metric="AAPL.filing_ratios",
                    value={key: round(value, 6) for key, value in ratios.items()},
                    unit="decimal",
                    formula="growth=current/previous-1; component_share=component/current",
                    assumptions=[
                        "USD millions from Apple 2025 Form 10-K research note.",
                        "Services revenue is used as the selected component.",
                    ],
                    data_status=DataStatus.PUBLIC_PARAPHRASE,
                )
            )
        return results

    def _terminal_message(self, policy: PolicyDecision) -> str:
        if policy.outcome == PolicyOutcome.HUMAN_REVIEW:
            return (
                "I cannot continue with product research in this context. Please pause financial "
                "decisions and contact a trusted person or qualified local support service."
            )
        return policy.rationale

    def research(self, request: ResearchRequest) -> ResearchResponse:
        selected = self._select_instruments(request.query, request.instrument_ids)
        profile, profile_changes = self.store.update_profile(request.session_id, request.profile)
        detected_intent, intent_confidence = intent.classify(request.query)
        if profile.current_task != detected_intent.value:
            profile_changes["current_task"] = {
                "from": profile.current_task,
                "to": detected_intent.value,
            }
        profile.current_task = detected_intent.value

        initial_policy = evaluate(request.query, detected_intent, profile, selected)
        required = required_profile_fields(detected_intent, selected)
        profile.missing_information = [field for field in required if not getattr(profile, field)]
        profile.confidence = self._profile_confidence(profile, required)
        profile = self.store.save_profile(request.session_id, profile)
        question_plan = clarification.plan(request.query, detected_intent, profile, selected)

        audit_id = f"wg-{uuid.uuid4().hex[:12]}"
        evidence = []
        calc_results: list[CalculationResult] = []
        claims = []
        conflicts = []
        limitations = [
            "Research profile is a prototype aid, not a regulatory suitability determination.",
            "Displayed price histories and portfolios are deterministic synthetic fixtures.",
        ]

        if initial_policy.outcome in {PolicyOutcome.REFUSE, PolicyOutcome.HUMAN_REVIEW}:
            message = self._terminal_message(initial_policy)
            final_policy = initial_policy
        elif question_plan.selected is not None:
            message = question_plan.selected.question
            final_policy = initial_policy
        else:
            final_policy = evaluate(
                request.query,
                detected_intent,
                profile,
                selected,
                include_missing=False,
            )
            evidence = self.retriever.search(
                request.query + " " + " ".join(instrument.symbol for instrument in selected),
                [instrument.instrument_id for instrument in selected],
            )
            if any(item.freshness in {"review_date", "stale", "future_dated"} for item in evidence):
                limitations.append("At least one source requires a date check before current use.")
            if any(item.data_status == DataStatus.SYNTHETIC for item in evidence):
                limitations.append("Some evidence cards are explicitly synthetic product fixtures.")
            conflicts = evidence_checks.detect_conflicts(evidence)
            if conflicts:
                final_policy = PolicyDecision(
                    outcome=PolicyOutcome.CAUTION,
                    hits=[
                        *final_policy.hits,
                        PolicyHit(
                            rule_id="SOURCE_CONFLICT",
                            severity="high",
                            message="Retrieved documents disagree on one or more structured facts.",
                        ),
                    ],
                    rationale="Conflicting source facts require date/version review before use.",
                )
                limitations.append("Conflicting source facts require human date and version review.")
            calc_results = self._calculation_results(selected)
            try:
                composition = self.provider.compose(request.query, evidence, final_policy)
            except RuntimeError:
                self.provider = MockProvider()
                limitations.append("Configured model provider failed; deterministic mock composition was used.")
                composition = self.provider.compose(request.query, evidence, final_policy)
            valid_claims = [
                claim for claim in composition.claims if self.retriever.validate_citations(claim.citation_ids)
            ]
            if len(valid_claims) != len(composition.claims):
                final_policy = PolicyDecision(
                    outcome=PolicyOutcome.CAUTION,
                    hits=[
                        *final_policy.hits,
                        PolicyHit(
                            rule_id="INVALID_CITATION",
                            severity="high",
                            message="One or more generated claims had an unknown citation and were removed.",
                        ),
                    ],
                    rationale="Generated claims were restricted to known evidence identifiers.",
                )
                limitations.append("Invalid generated citations were removed before display.")
            claims = valid_claims
            message = composition.message if valid_claims else "I do not have enough validated evidence to answer."

        event = AuditEvent(
            audit_id=audit_id,
            timestamp=datetime.now(UTC),
            session_id=request.session_id,
            query=request.query,
            intent=detected_intent,
            outcome=final_policy.outcome,
            profile_changes=profile_changes,
            clarification=question_plan if question_plan.selected else None,
            policy_hits=final_policy.hits,
            evidence_ids=[item.document_id for item in evidence],
            calculation_metrics=[item.metric for item in calc_results],
            provider=self.provider.name,
            model=self.provider.model,
            prompt_version=PROMPT_VERSION,
        )
        self.store.append_audit(event)
        return ResearchResponse(
            session_id=request.session_id,
            intent=detected_intent,
            outcome=final_policy.outcome,
            message=message,
            disclaimer=DISCLAIMER,
            task_confidence=round(intent_confidence * (0.6 + 0.4 * profile.confidence), 4),
            profile=profile,
            clarification=question_plan if question_plan.selected else None,
            evidence=evidence,
            conflicts=conflicts,
            calculations=calc_results,
            claims=claims,
            policy=final_policy,
            audit_id=audit_id,
            limitations=limitations,
        )

    def compare(self, request: CompareRequest) -> CompareResponse:
        unknown = [item for item in request.instrument_ids if item.upper() not in self.instruments]
        if unknown:
            raise ValueError("unknown instrument ids: " + ", ".join(unknown))
        instruments = [self.instruments[item.upper()] for item in request.instrument_ids]
        metrics: dict[str, dict[str, CalculationResult]] = {}
        for instrument in instruments:
            prices = synthetic_prices(instrument.instrument_id)
            metrics[instrument.instrument_id] = {
                "annualized_return": CalculationResult(
                    metric="annualized_return",
                    value=round(calculations.annualized_return(prices), 6),
                    unit="decimal per year",
                    formula="(last / first) ** (12 / periods) - 1",
                    assumptions=["Fixed-seed synthetic monthly series; not historical performance."],
                ),
                "annualized_volatility": CalculationResult(
                    metric="annualized_volatility",
                    value=round(calculations.annualized_volatility(prices), 6),
                    unit="decimal per year",
                    formula="stdev(periodic returns) * sqrt(12)",
                    assumptions=["Fixed-seed synthetic monthly series; not historical performance."],
                ),
                "maximum_drawdown": CalculationResult(
                    metric="maximum_drawdown",
                    value=round(calculations.maximum_drawdown(prices), 6),
                    unit="decimal",
                    formula="min(price / running_peak - 1)",
                    assumptions=["Fixed-seed synthetic monthly series; not historical performance."],
                ),
                "expense_ratio": CalculationResult(
                    metric="expense_ratio",
                    value=instrument.expense_ratio,
                    unit="decimal per year",
                    formula="dated instrument metadata",
                    assumptions=[f"Metadata as of {instrument.as_of.isoformat()}."],
                    data_status=instrument.data_status,
                ),
                "liquidity_days": CalculationResult(
                    metric="liquidity_days",
                    value=float(instrument.liquidity_days),
                    unit="business days",
                    formula="dated instrument metadata",
                    assumptions=["Metadata includes a fixture as-of date; verify public documents separately."],
                    data_status=instrument.data_status,
                ),
            }
        notes = [
            "Synthetic return, volatility and drawdown series support calculation testing only.",
            "Instrument types, currencies, risks and source dates differ; no overall best product is inferred.",
            "Expense ratios can omit transaction, tax, spread, advice and other costs.",
        ]
        return CompareResponse(
            instruments=instruments,
            metrics=metrics,
            comparability_notes=notes,
            disclaimer=DISCLAIMER,
        )

    def portfolio(self, request: PortfolioRequest) -> PortfolioResponse:
        unknown = [
            item.instrument_id for item in request.holdings if item.instrument_id.upper() not in self.instruments
        ]
        if unknown:
            raise ValueError("unknown instrument ids: " + ", ".join(unknown))
        resolved = [(holding, self.instruments[holding.instrument_id.upper()]) for holding in request.holdings]
        weights = [holding.weight for holding, _ in resolved]
        concentration = calculations.concentration_ratio(weights)
        sector = calculations.aggregate_exposure((holding.weight, item.sectors) for holding, item in resolved)
        region = calculations.aggregate_exposure((holding.weight, item.regions) for holding, item in resolved)
        currency: dict[str, float] = {}
        for holding, item in resolved:
            currency[item.currency] = round(currency.get(item.currency, 0.0) + holding.weight, 10)
        price_paths = [synthetic_prices(item.instrument_id) for _, item in resolved]
        portfolio_prices = [
            sum(
                holding.weight * path[index] / path[0] for (holding, _), path in zip(resolved, price_paths, strict=True)
            )
            for index in range(len(price_paths[0]))
        ]
        shocks = [request.scenario_shock * item.risk_level / 5.0 for _, item in resolved]
        loss = calculations.scenario_loss(weights, shocks)
        results = [
            CalculationResult(
                metric="portfolio_concentration",
                value={key: round(value, 6) for key, value in concentration.items()},
                unit="decimal",
                formula="largest, top-three and Herfindahl concentration measures",
                assumptions=["Holding weights are synthetic and sum to one."],
            ),
            CalculationResult(
                metric="portfolio_annualized_volatility",
                value=round(calculations.annualized_volatility(portfolio_prices), 6),
                unit="decimal per year",
                formula="stdev(weighted synthetic portfolio returns) * sqrt(12)",
                assumptions=[
                    "Static weights and fixed-seed synthetic monthly series.",
                    "No rebalancing, costs, cash flows, or historical-performance claim.",
                ],
            ),
            CalculationResult(
                metric="portfolio_maximum_drawdown",
                value=round(calculations.maximum_drawdown(portfolio_prices), 6),
                unit="decimal drawdown",
                formula="min(weighted_index / running_peak - 1)",
                assumptions=[
                    "Static weights and fixed-seed synthetic monthly series.",
                    "This is not a forecast or a complete portfolio risk model.",
                ],
            ),
            CalculationResult(
                metric="simple_scenario_loss",
                value=round(loss, 6),
                unit="decimal portfolio change",
                formula="sum(weight * risk_scaled_shock)",
                assumptions=[
                    f"Base illustrative shock {request.scenario_shock:.1%}, scaled linearly by risk level.",
                    "This is not VaR, stress-testing certification or a forecast.",
                ],
            ),
        ]
        return PortfolioResponse(
            calculations=results,
            sector_exposure=sector,
            region_exposure=region,
            currency_exposure=dict(sorted(currency.items())),
            disclaimer=DISCLAIMER,
        )
