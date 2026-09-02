"""Run the fixed 39-case official citation traceability evaluation."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from wealthguard.official_ingestion import ROOT, file_sha256, load_chunks, load_manifest

RESULT_PATH = ROOT / "results" / "citation_evaluation.json"

sources = load_manifest()
chunks = load_chunks()
by_document = {source.document_id: [] for source in sources}
for chunk in chunks:
    by_document[chunk.document_id].append(chunk)

cases = []
for source in sources:
    candidates = by_document[source.document_id]
    indexes = [0, len(candidates) // 2, len(candidates) - 1]
    for sample_number, index in enumerate(indexes, start=1):
        chunk = candidates[index]
        raw_path = ROOT / source.raw_path
        checks = {
            "document_checksum": file_sha256(raw_path) == source.sha256,
            "chunk_checksum": hashlib.sha256(chunk.text.encode("utf-8")).hexdigest() == chunk.text_sha256,
            "document_link": chunk.document_id == source.document_id,
            "source_link": chunk.source_url == source.source_url,
            "date_present_or_declared_undated": bool(chunk.published_at) or chunk.version_status == "undated",
            "location_present": bool(chunk.page_number or chunk.paragraph_start),
            "excerpt_present": bool(chunk.text.strip()),
        }
        cases.append(
            {
                "case_id": f"{source.document_id}-TRACE-{sample_number}",
                "chunk_id": chunk.chunk_id,
                "passed": all(checks.values()),
                "checks": checks,
            }
        )

report = {
    "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
    "scope": "Three deterministic citation-trace samples from each of 13 official documents.",
    "cases": len(cases),
    "passed": sum(case["passed"] for case in cases),
    "failed": sum(not case["passed"] for case in cases),
    "documents": len(sources),
    "chunks": len(chunks),
    "cases_detail": cases,
}
RESULT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Citation traceability: {report['passed']}/{report['cases']} passed across {len(sources)} documents")
