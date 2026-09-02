"""Response-composer boundary with a safe, deterministic mock provider."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from .models import CitedClaim, Evidence, PolicyDecision

PROMPT_VERSION = "wealthguard-research-v1"


@dataclass(frozen=True)
class Composition:
    message: str
    claims: list[CitedClaim]


class Provider(Protocol):
    name: str
    model: str

    def compose(self, query: str, evidence: list[Evidence], policy: PolicyDecision) -> Composition: ...


class MockProvider:
    name = "mock"
    model = "mock-evidence-composer-v1"

    def compose(self, query: str, evidence: list[Evidence], policy: PolicyDecision) -> Composition:
        claims: list[CitedClaim] = []
        for item in evidence[:3]:
            sentence = item.excerpt.split(". ")[0].strip().rstrip(".") + "."
            claims.append(
                CitedClaim(
                    text=sentence,
                    citation_ids=[item.document_id],
                    synthetic=item.data_status.value.startswith("synthetic"),
                )
            )
        if not claims:
            return Composition(
                message="I do not have enough dated evidence to answer this research question.",
                claims=[],
            )
        prefix = "Research view only"
        if policy.outcome.value in {"caution", "educational_only"}:
            prefix += f" ({policy.outcome.value.replace('_', ' ')})"
        body = " ".join(claim.text for claim in claims)
        return Composition(
            message=(
                f"{prefix}: {body} Review the cited document dates and the limitations before drawing a conclusion."
            ),
            claims=claims,
        )


class OpenAICompatibleProvider:
    """Optional provider. Policy, arithmetic and citation validity remain outside the model."""

    name = "openai-compatible"

    def __init__(self) -> None:
        self.model = os.environ.get("WEALTHGUARD_LLM_MODEL", "")
        self.base_url = os.environ.get("WEALTHGUARD_LLM_BASE_URL", "").rstrip("/")
        self.key = os.environ.get("WEALTHGUARD_LLM_API_KEY", "")
        self.timeout = float(os.environ.get("WEALTHGUARD_LLM_TIMEOUT", "12"))

    def compose(self, query: str, evidence: list[Evidence], policy: PolicyDecision) -> Composition:
        if not self.model or not self.base_url or not self.key:
            raise RuntimeError("optional provider is not configured")
        facts = [
            {
                "citation_id": item.document_id,
                "text": item.excerpt,
                "published_at": str(item.published_at),
            }
            for item in evidence
        ]
        prompt = (
            "Answer as an educational research assistant. Use only the supplied facts. "
            "Do not give buy/sell/hold instructions, forecasts or guaranteed returns. "
            "Return JSON with message and claims; each claim has text and citation_ids.\n"
            f"Policy outcome: {policy.outcome.value}\nQuestion: {query}\nFacts: {json.dumps(facts)}"
        )
        payload = {
            "model": self.model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": prompt}],
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
            output = json.loads(body["choices"][0]["message"]["content"])
            claims = [CitedClaim(**claim) for claim in output.get("claims", [])]
            return Composition(message=str(output["message"]), claims=claims)
        except (
            urllib.error.URLError,
            TimeoutError,
            KeyError,
            ValueError,
            TypeError,
            OSError,
        ) as exc:
            raise RuntimeError("optional model provider failed") from exc


def provider_from_environment() -> Provider:
    provider = os.environ.get("WEALTHGUARD_LLM_PROVIDER", "mock").strip().lower()
    if provider == "openai-compatible":
        return OpenAICompatibleProvider()
    return MockProvider()
