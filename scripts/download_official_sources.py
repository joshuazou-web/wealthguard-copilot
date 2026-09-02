"""Download the allowlisted official-source catalog into a reproducible offline pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "official" / "source_catalog.json"
RAW_DIR = ROOT / "data" / "official" / "raw"
MANIFEST_PATH = ROOT / "data" / "official" / "manifest.json"
ALLOWED_HOSTS = {
    "www.sec.gov",
    "www.hkex.com.hk",
    "www.hkexgroup.com",
    "disc.static.szse.cn",
    "investor.szse.cn",
    "www.szse.cn",
    "www.csrc.gov.cn",
}
USER_AGENT = "WealthGuardCopilot/0.1 research@example.com"
MAX_BYTES = 60 * 1024 * 1024


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _download(url: str) -> tuple[bytes, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError(f"URL is not an allowlisted HTTPS official source: {url}")
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/pdf",
            "Accept-Encoding": "identity",
            "Connection": "close",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        content = response.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError(f"source exceeds {MAX_BYTES} bytes: {url}")
        media_type = response.headers.get_content_type()
    return content, media_type


def download_catalog(force: bool = False) -> list[dict[str, object]]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    retrieved_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    prior_records = {}
    if MANIFEST_PATH.exists():
        prior_records = {item["document_id"]: item for item in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))}
    for index, entry in enumerate(catalog, start=1):
        target = RAW_DIR / entry["raw_filename"]
        if target.exists() and not force:
            content = target.read_bytes()
            prior = prior_records.get(entry["document_id"])
            if prior is None:
                raise ValueError(f"unmanifested existing file; use --force after review: {target}")
            if sha256_bytes(content) != prior["sha256"]:
                raise ValueError(f"existing official file checksum mismatch: {entry['document_id']}")
            media_type = prior["media_type"]
            item_retrieved_at = prior["retrieved_at"]
            status = "reused"
        else:
            content, media_type = _download(entry["source_url"])
            if not (
                media_type.startswith(entry["expected_media_type"])
                or (entry["expected_media_type"] == "text/html" and media_type == "application/octet-stream")
            ):
                raise ValueError(f"unexpected media type {media_type} for {entry['document_id']}")
            with tempfile.NamedTemporaryFile(dir=RAW_DIR, prefix=".download-", delete=False) as handle:
                handle.write(content)
                temporary = Path(handle.name)
            os.replace(temporary, target)
            item_retrieved_at = retrieved_at
            status = "downloaded"
        record = {
            **entry,
            "raw_path": target.relative_to(ROOT).as_posix(),
            "retrieved_at": item_retrieved_at,
            "media_type": media_type,
            "size_bytes": len(content),
            "sha256": sha256_bytes(content),
        }
        records.append(record)
        print(
            f"[{index:02}/{len(catalog)}] {status:10} {entry['document_id']} ({len(content):,} bytes)",
            flush=True,
        )
    MANIFEST_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST_PATH} with {len(records)} verified source records")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="replace existing raw files from the allowlisted URLs")
    arguments = parser.parse_args()
    download_catalog(force=arguments.force)
