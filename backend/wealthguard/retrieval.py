"""Small, deterministic retrieval layer with dated citations."""

from __future__ import annotations

import math
import re
from collections import Counter
from datetime import date

from .models import Evidence, ResearchDocument

_TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "should",
    "the",
    "this",
    "to",
    "what",
    "with",
}


def tokens(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN.findall(text) if token.lower() not in _STOP]


class Retriever:
    def __init__(self, documents: list[ResearchDocument], today: date | None = None) -> None:
        self.documents = documents
        self.today = today or date.today()
        self._terms = [Counter(tokens(document.content + " " + " ".join(document.key_facts))) for document in documents]
        self._df: Counter[str] = Counter()
        for terms in self._terms:
            self._df.update(terms.keys())

    def _idf(self, term: str) -> float:
        return math.log((len(self.documents) + 1) / (self._df[term] + 0.5)) + 1.0

    def freshness(self, document: ResearchDocument) -> str:
        age_days = (self.today - document.published_at).days
        if age_days < 0:
            return "future_dated"
        if age_days <= 550:
            return "current_for_demo"
        if age_days <= 1100:
            return "review_date"
        return "stale"

    def search(self, query: str, instrument_ids: list[str], limit: int = 4) -> list[Evidence]:
        query_terms = Counter(tokens(query))
        scored: list[tuple[float, ResearchDocument]] = []
        for document, term_counts in zip(self.documents, self._terms, strict=True):
            lexical = sum(
                query_weight * self._idf(term) * min(term_counts.get(term, 0), 3)
                for term, query_weight in query_terms.items()
            )
            instrument_boost = 4.0 if document.instrument_id in instrument_ids else 0.0
            general_boost = 0.45 if document.instrument_id is None else 0.0
            score = lexical + instrument_boost + general_boost
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: (-item[0], item[1].document_id))
        if not scored:
            scored = [(0.1, document) for document in self.documents if document.instrument_id is None]

        evidence: list[Evidence] = []
        for score, document in scored[:limit]:
            evidence.append(
                Evidence(
                    document_id=document.document_id,
                    instrument_id=document.instrument_id,
                    title=document.title,
                    document_type=document.document_type,
                    source_name=document.source_name,
                    source_url=document.source_url,
                    published_at=document.published_at,
                    retrieved_at=document.retrieved_at,
                    excerpt=document.content,
                    structured_facts=document.structured_facts,
                    score=round(score, 6),
                    freshness=self.freshness(document),
                    data_status=document.data_status,
                )
            )
        return evidence

    def validate_citations(self, citation_ids: list[str]) -> bool:
        known = {document.document_id for document in self.documents}
        return bool(citation_ids) and set(citation_ids).issubset(known)
