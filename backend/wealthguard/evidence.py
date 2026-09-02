"""Deterministic evidence checks performed after retrieval and before composition."""

from __future__ import annotations

from collections import defaultdict

from .models import Evidence, EvidenceConflict


def detect_conflicts(evidence: list[Evidence]) -> list[EvidenceConflict]:
    observed: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for item in evidence:
        if not item.instrument_id:
            continue
        for fact_key, value in item.structured_facts.items():
            observed[(item.instrument_id, fact_key)][value].append(item.document_id)

    conflicts: list[EvidenceConflict] = []
    for (instrument_id, fact_key), values in sorted(observed.items()):
        if len(values) <= 1:
            continue
        documents = sorted(document_id for identifiers in values.values() for document_id in identifiers)
        conflicts.append(
            EvidenceConflict(
                instrument_id=instrument_id,
                fact_key=fact_key,
                values={value: ", ".join(sorted(ids)) for value, ids in sorted(values.items())},
                document_ids=documents,
            )
        )
    return conflicts
