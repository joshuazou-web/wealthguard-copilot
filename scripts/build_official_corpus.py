"""Verify raw official files and build deterministic page/paragraph chunks."""

from wealthguard.official_ingestion import build_chunks, load_manifest, save_chunks

sources = load_manifest()
chunks = build_chunks(sources)
save_chunks(chunks)
print(f"Verified {len(sources)} official documents and wrote {len(chunks)} chunks")
