"""Small, deterministic retrieval layer with dated citations."""

from __future__ import annotations

import math
import re
from collections import Counter
from datetime import date

from .models import DocumentChunk, Evidence, ResearchDocument

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
    def __init__(
        self,
        documents: list[ResearchDocument],
        today: date | None = None,
        chunks: list[DocumentChunk] | None = None,
    ) -> None:
        self.documents = documents
        self.today = today or date.today()
        self.chunks = chunks or []
        self._chunks_by_id = {chunk.chunk_id: chunk for chunk in self.chunks}
        corpus = [chunk.text for chunk in self.chunks] + [
            document.content + " " + " ".join(document.key_facts) for document in documents
        ]
        self._corpus_size = len(corpus)
        self._terms = [Counter(tokens(text)) for text in corpus]
        self._df: Counter[str] = Counter()
        for terms in self._terms:
            self._df.update(terms.keys())

    def _idf(self, term: str) -> float:
        return math.log((self._corpus_size + 1) / (self._df[term] + 0.5)) + 1.0

    def freshness(self, published_at: date | None) -> str:
        if published_at is None:
            return "undated"
        age_days = (self.today - published_at).days
        if age_days < 0:
            return "future_dated"
        if age_days <= 550:
            return "current_for_demo"
        if age_days <= 1100:
            return "review_date"
        return "stale"

    def search(self, query: str, instrument_ids: list[str], limit: int = 4) -> list[Evidence]:
        query_terms = Counter(tokens(query))
        items: list[DocumentChunk | ResearchDocument] = [*self.chunks, *self.documents]
        scored: list[tuple[float, DocumentChunk | ResearchDocument]] = []
        for document, term_counts in zip(items, self._terms, strict=True):
            lexical = sum(
                query_weight * self._idf(term) * min(term_counts.get(term, 0), 3)
                for term, query_weight in query_terms.items()
            )
            instrument_boost = 4.0 if document.instrument_id in instrument_ids else 0.0
            general_boost = 0.25 if document.instrument_id is None else 0.0
            score = lexical + instrument_boost + general_boost
            if score > 0:
                scored.append((score, document))
        scored.sort(key=lambda item: (-item[0], getattr(item[1], "chunk_id", item[1].document_id)))
        if not scored:
            scored = [(0.1, document) for document in items if document.instrument_id is None]

        evidence: list[Evidence] = []
        used_documents: set[str] = set()
        for score, document in scored:
            if document.document_id in used_documents:
                continue
            used_documents.add(document.document_id)
            is_chunk = isinstance(document, DocumentChunk)
            excerpt = document.text if is_chunk else document.content
            excerpt = excerpt[:900].rstrip() + ("…" if len(excerpt) > 900 else "")
            evidence.append(
                Evidence(
                    chunk_id=document.chunk_id if is_chunk else document.document_id,
                    document_id=document.document_id,
                    instrument_id=document.instrument_id,
                    title=document.title,
                    document_type=document.document_type,
                    source_name=document.source_name,
                    source_url=document.source_url,
                    published_at=document.published_at,
                    retrieved_at=document.retrieved_at,
                    excerpt=excerpt,
                    structured_facts=document.structured_facts,
                    score=round(score, 6),
                    freshness=self.freshness(document.published_at),
                    data_status=document.data_status,
                    version=document.version if is_chunk else None,
                    version_status=document.version_status if is_chunk else "legacy_fixture",
                    page_number=document.page_number if is_chunk else None,
                    section=document.section if is_chunk else None,
                    paragraph_start=document.paragraph_start if is_chunk else None,
                    paragraph_end=document.paragraph_end if is_chunk else None,
                    source_line_start=document.source_line_start if is_chunk else None,
                    source_line_end=document.source_line_end if is_chunk else None,
                    locator_url=(
                        f"/api/evidence/open?chunk_id={document.chunk_id}" if is_chunk else document.source_url
                    ),
                    document_sha256=document.document_sha256 if is_chunk else document.checksum,
                )
            )
            if len(evidence) >= limit:
                break
        return evidence

    def validate_citations(self, citation_ids: list[str]) -> bool:
        known = {document.document_id for document in self.documents} | {chunk.chunk_id for chunk in self.chunks}
        return bool(citation_ids) and set(citation_ids).issubset(known)

    def chunk(self, chunk_id: str) -> DocumentChunk | None:
        return self._chunks_by_id.get(chunk_id)
