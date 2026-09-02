"""Validation boundary for offline research-document ingestion."""

from __future__ import annotations

import hashlib
from urllib.parse import urlparse

from .models import ResearchDocument


def ingest_documents(documents: list[ResearchDocument]) -> list[ResearchDocument]:
    identifiers: set[str] = set()
    validated: list[ResearchDocument] = []
    for document in documents:
        if document.document_id in identifiers:
            raise ValueError(f"duplicate document id: {document.document_id}")
        identifiers.add(document.document_id)
        parsed = urlparse(document.source_url)
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(f"document source must be an HTTPS URL: {document.document_id}")
        if document.published_at > document.retrieved_at:
            raise ValueError(f"document publication date follows retrieval date: {document.document_id}")
        checksum = hashlib.sha256(document.content.encode("utf-8")).hexdigest()
        if checksum != document.checksum:
            raise ValueError(f"document checksum mismatch: {document.document_id}")
        validated.append(document.model_copy(deep=True))
    return validated
