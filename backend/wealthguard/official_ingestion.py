"""Verified offline ingestion for official PDF and HTML source files."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

from .models import DocumentChunk, OfficialSourceDocument

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "data" / "official" / "manifest.json"
CHUNKS_PATH = ROOT / "data" / "official" / "processed" / "chunks.jsonl"
_SPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class Paragraph:
    text: str
    page_number: int | None
    section: str | None
    source_line_start: int | None
    source_line_end: int | None


class _BlockHTMLParser(HTMLParser):
    BLOCKS = {"p", "li", "td", "th", "h1", "h2", "h3", "h4", "h5", "h6"}
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active_tag: str | None = None
        self.active_line: int | None = None
        self.buffer: list[str] = []
        self.section: str | None = None
        self.paragraphs: list[Paragraph] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP:
            self.depth += 1
            return
        if self.depth or tag not in self.BLOCKS:
            return
        self.active_tag = tag
        self.active_line = self.getpos()[0]
        self.buffer = []

    def handle_data(self, data: str) -> None:
        if not self.depth and self.active_tag:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP and self.depth:
            self.depth -= 1
            return
        if self.depth or tag != self.active_tag:
            return
        text = _SPACE.sub(" ", " ".join(self.buffer)).strip()
        if text and len(text) >= 3:
            if tag.startswith("h"):
                self.section = text[:240]
            self.paragraphs.append(Paragraph(text, None, self.section, self.active_line, self.getpos()[0]))
        self.active_tag = None
        self.active_line = None
        self.buffer = []


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_source_file(source: OfficialSourceDocument, path: Path) -> None:
    if not path.is_file():
        raise ValueError(f"official source file is missing: {source.document_id}")
    if file_sha256(path) != source.sha256:
        raise ValueError(f"official file checksum mismatch: {source.document_id}")


def load_manifest(path: Path = MANIFEST_PATH, *, verify_files: bool = True) -> list[OfficialSourceDocument]:
    records = json.loads(path.read_text(encoding="utf-8"))
    sources = [OfficialSourceDocument(**record) for record in records]
    seen: set[str] = set()
    raw_root = (ROOT / "data" / "official" / "raw").resolve()
    for source in sources:
        if source.document_id in seen:
            raise ValueError(f"duplicate official document id: {source.document_id}")
        seen.add(source.document_id)
        raw_path = (ROOT / source.raw_path).resolve()
        if raw_root not in raw_path.parents:
            raise ValueError(f"official raw path escapes the pack: {source.document_id}")
        if verify_files:
            verify_source_file(source, raw_path)
    return sources


def _pdf_paragraphs(path: Path) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    for page_number, page in enumerate(PdfReader(path).pages, start=1):
        text = page.extract_text() or ""
        page_items = [_SPACE.sub(" ", value).strip() for value in re.split(r"\n\s*\n|(?<=\.)\s*\n", text)]
        page_items = [value for value in page_items if len(value) >= 3]
        if not page_items and text.strip():
            page_items = [_SPACE.sub(" ", text).strip()]
        for value in page_items:
            paragraphs.append(Paragraph(value, page_number, None, None, None))
    return paragraphs


def _html_paragraphs(path: Path) -> list[Paragraph]:
    content = path.read_bytes()
    for encoding in ("utf-8", "gb18030", "big5"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = content.decode("utf-8", errors="replace")
    parser = _BlockHTMLParser()
    parser.feed(text)
    unique: list[Paragraph] = []
    seen: set[tuple[str, int | None]] = set()
    for paragraph in parser.paragraphs:
        key = (paragraph.text, paragraph.source_line_start)
        if key not in seen:
            seen.add(key)
            unique.append(paragraph)
    return unique


def extract_paragraphs(source: OfficialSourceDocument) -> list[Paragraph]:
    path = ROOT / source.raw_path
    if source.media_type == "application/pdf" or path.suffix.lower() == ".pdf":
        return _pdf_paragraphs(path)
    return _html_paragraphs(path)


def _version_statuses(sources: list[OfficialSourceDocument]) -> dict[str, str]:
    groups: dict[tuple[str, str], list[OfficialSourceDocument]] = {}
    for source in sources:
        family = source.instrument_id or source.document_id
        groups.setdefault((family, source.document_type), []).append(source)
    statuses: dict[str, str] = {}
    for group in groups.values():
        dated = [item for item in group if item.published_at]
        latest = max((item.published_at for item in dated), default=None)
        for item in group:
            statuses[item.document_id] = (
                "latest" if item.published_at and item.published_at == latest else "older_version"
            )
            if item.published_at is None:
                statuses[item.document_id] = "undated"
    return statuses


def build_chunks(sources: list[OfficialSourceDocument], target_chars: int = 1100) -> list[DocumentChunk]:
    statuses = _version_statuses(sources)
    chunks: list[DocumentChunk] = []
    for source in sources:
        paragraphs = extract_paragraphs(source)
        ordinal = 0
        bucket: list[tuple[int, Paragraph]] = []
        bucket_chars = 0

        def flush(current_source: OfficialSourceDocument = source) -> None:
            nonlocal ordinal, bucket, bucket_chars
            if not bucket:
                return
            ordinal += 1
            text = "\n".join(item.text for _, item in bucket)
            first_number, first = bucket[0]
            last_number, last = bucket[-1]
            page = first.page_number if all(item.page_number == first.page_number for _, item in bucket) else None
            location = f"p{page}" if page else f"para{first_number}-{last_number}"
            chunk_id = f"{current_source.document_id}:{location}:c{ordinal}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=current_source.document_id,
                    instrument_id=current_source.instrument_id,
                    title=current_source.title,
                    document_type=current_source.document_type,
                    source_name=current_source.source_name,
                    source_url=current_source.source_url,
                    published_at=current_source.published_at,
                    retrieved_at=current_source.retrieved_at.date(),
                    version=current_source.version,
                    version_status=statuses[current_source.document_id],
                    document_sha256=current_source.sha256,
                    ordinal=ordinal,
                    text=text,
                    text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    page_number=page,
                    section=first.section,
                    paragraph_start=first_number,
                    paragraph_end=last_number,
                    source_line_start=first.source_line_start,
                    source_line_end=last.source_line_end,
                )
            )
            bucket = []
            bucket_chars = 0

        for paragraph_number, paragraph in enumerate(paragraphs, start=1):
            boundary = bucket and (
                paragraph.page_number != bucket[-1][1].page_number
                or paragraph.section != bucket[-1][1].section
                or bucket_chars + len(paragraph.text) > target_chars
            )
            if boundary:
                flush()
            bucket.append((paragraph_number, paragraph))
            bucket_chars += len(paragraph.text)
        flush()
        if ordinal == 0:
            raise ValueError(f"no extractable text in official source: {source.document_id}")
    return chunks


def save_chunks(chunks: list[DocumentChunk], path: Path = CHUNKS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(chunk.model_dump(mode="json"), ensure_ascii=False) + "\n" for chunk in chunks),
        encoding="utf-8",
    )


def load_chunks(path: Path = CHUNKS_PATH) -> list[DocumentChunk]:
    chunks = [DocumentChunk.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    known_sources = {source.document_id: source for source in load_manifest()}
    for chunk in chunks:
        source = known_sources.get(chunk.document_id)
        if source is None or chunk.document_sha256 != source.sha256:
            raise ValueError(f"chunk references an unknown or changed document: {chunk.chunk_id}")
        if hashlib.sha256(chunk.text.encode("utf-8")).hexdigest() != chunk.text_sha256:
            raise ValueError(f"official chunk checksum mismatch: {chunk.chunk_id}")
    return chunks
