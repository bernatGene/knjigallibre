from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

from .anchors import build_line_starts, offset_to_line_col
from .config import ParserConfig
from .models import Block, BlockManifest

PARSER_VERSION = "1.0.0"
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?…»\"'])\s+")


def source_sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def config_hash(config: ParserConfig) -> str:
    payload = json.dumps(asdict(config), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def manifest_path_for_source(source_path: Path) -> Path:
    return source_path.with_suffix(".blocks.json")


def _is_dialogue_line(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith(("-", "–", "—"))


def _looks_like_toc_entry(line: str) -> bool:
    stripped = line.strip()
    return "." in stripped and re.search(r"\b\d+\s*$", stripped) is not None


def _build_control_patterns(config: ParserConfig) -> list[re.Pattern[str]]:
    return [re.compile(pattern, re.IGNORECASE) for pattern in config.control_line_patterns]


def _is_control_line(line: str, patterns: list[re.Pattern[str]]) -> bool:
    stripped = line.strip().replace("\x0c", "").strip()
    if not stripped:
        return True
    if _looks_like_toc_entry(stripped):
        return True
    return any(pattern.match(stripped) for pattern in patterns)


def _line_segments(raw: str) -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    for match in re.finditer(r".*(?:\n|$)", raw):
        segment = match.group(0)
        if not segment and match.start() == len(raw):
            continue
        out.append((segment, match.start(), match.end()))
    return out


def _normalize_line_text(line: str) -> str:
    text = line.replace("\r", "").replace("\x0c", "")
    text = text.rstrip("\n")
    return re.sub(r"\s+", " ", text).strip()


def _parse_paragraph_units(raw: str, config: ParserConfig) -> list[dict[str, object]]:
    patterns = _build_control_patterns(config)
    segments = _line_segments(raw)

    units: list[dict[str, object]] = []
    current_text_parts: list[str] = []
    current_start: int | None = None
    current_end: int | None = None
    current_is_dialogue = False

    def flush() -> None:
        nonlocal current_text_parts, current_start, current_end, current_is_dialogue
        if not current_text_parts or current_start is None or current_end is None:
            current_text_parts = []
            current_start = None
            current_end = None
            current_is_dialogue = False
            return
        text = re.sub(r"\s+", " ", " ".join(current_text_parts)).strip()
        if text:
            units.append(
                {
                    "text": text,
                    "start": current_start,
                    "end": current_end,
                    "dialogue": current_is_dialogue,
                }
            )
        current_text_parts = []
        current_start = None
        current_end = None
        current_is_dialogue = False

    for segment, seg_start, seg_end in segments:
        line_text = _normalize_line_text(segment)
        if not line_text:
            flush()
            continue

        if config.drop_control_lines and _is_control_line(line_text, patterns):
            flush()
            continue

        if current_start is None:
            current_start = seg_start
            current_is_dialogue = _is_dialogue_line(line_text)

        if (
            config.merge_hyphenated_linebreaks
            and current_text_parts
            and current_text_parts[-1].endswith("-")
            and line_text
            and line_text[0].isalpha()
        ):
            current_text_parts[-1] = current_text_parts[-1][:-1] + line_text
        else:
            current_text_parts.append(line_text)
        current_end = seg_end

    flush()
    return units


def _split_paragraph_by_sentence(text: str, start: int, end: int, config: ParserConfig) -> list[tuple[str, int, int]]:
    if not config.split_long_paragraphs or len(text) <= config.max_block_chars:
        return [(text, start, end)]

    sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(text) if s.strip()]
    if len(sentences) <= 1:
        return [(text, start, end)]

    chunks: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        candidate = " ".join(current + [sentence]).strip()
        if current and len(candidate) > config.max_block_chars:
            chunks.append(" ".join(current).strip())
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        chunks.append(" ".join(current).strip())

    if not chunks:
        return [(text, start, end)]

    raw_span_len = max(1, end - start)
    total_len = max(1, sum(len(chunk) for chunk in chunks))
    mapped: list[tuple[str, int, int]] = []
    cursor = start
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            chunk_end = end
        else:
            proportion = len(chunk) / total_len
            chunk_len = max(1, int(raw_span_len * proportion))
            chunk_end = min(end, cursor + chunk_len)
        mapped.append((chunk, cursor, chunk_end))
        cursor = chunk_end

    return mapped


def _merge_short_consecutive_chunks(chunks: list[dict[str, object]], config: ParserConfig) -> list[dict[str, object]]:
    if not chunks:
        return []

    merged: list[dict[str, object]] = []
    for chunk in chunks:
        if not merged:
            merged.append(dict(chunk))
            continue

        prev = merged[-1]
        if str(prev["kind"]) != str(chunk["kind"]):
            merged.append(dict(chunk))
            continue

        combined_text = f"{prev['text']} {chunk['text']}".strip()
        if len(combined_text) <= config.max_block_chars:
            prev["text"] = combined_text
            prev["end"] = int(chunk["end"])
            continue

        merged.append(dict(chunk))

    return merged


def parse_text_to_blocks(raw: str, config: ParserConfig | None = None) -> list[Block]:
    cfg = config or ParserConfig()
    units = _parse_paragraph_units(raw, cfg)
    line_starts = build_line_starts(raw)

    grouped: list[dict[str, object]] = []
    for unit in units:
        unit_text = str(unit["text"])
        unit_start = int(unit["start"])
        unit_end = int(unit["end"])
        is_dialogue = bool(unit["dialogue"])

        if cfg.group_dialogue and is_dialogue and grouped:
            last = grouped[-1]
            if bool(last["dialogue"]) and len(str(last["text"])) + 1 + len(unit_text) <= cfg.max_block_chars:
                last["text"] = f"{last['text']} {unit_text}".strip()
                last["end"] = unit_end
                continue

        grouped.append(
            {
                "text": unit_text,
                "start": unit_start,
                "end": unit_end,
                "dialogue": is_dialogue,
            }
        )

    chunk_items: list[dict[str, object]] = []
    for item in grouped:
        chunks = _split_paragraph_by_sentence(
            str(item["text"]), int(item["start"]), int(item["end"]), cfg
        )
        for chunk_text, chunk_start, chunk_end in chunks:
            if len(chunk_text.split()) < cfg.min_words_per_block:
                continue
            chunk_items.append(
                {
                    "text": chunk_text,
                    "start": chunk_start,
                    "end": chunk_end,
                    "kind": "dialogue" if bool(item["dialogue"]) else "narration",
                }
            )

    merged_chunks = _merge_short_consecutive_chunks(chunk_items, cfg)

    blocks: list[Block] = []
    for item in merged_chunks:
        chunk_text = str(item["text"])
        chunk_start = int(item["start"])
        chunk_end = int(item["end"])
        start_line, start_col = offset_to_line_col(raw, line_starts, chunk_start)
        end_line, end_col = offset_to_line_col(raw, line_starts, chunk_end)
        index = len(blocks)
        blocks.append(
            Block(
                block_id=f"b{index:05d}",
                index=index,
                text=chunk_text,
                start_offset=chunk_start,
                end_offset=chunk_end,
                start_line=start_line,
                start_col=start_col,
                end_line=end_line,
                end_col=end_col,
                kind=str(item["kind"]),
            )
        )
    return blocks


def build_manifest(raw: str, source_path: Path, config: ParserConfig | None = None) -> BlockManifest:
    cfg = config or ParserConfig()
    blocks = parse_text_to_blocks(raw, cfg)
    return BlockManifest(
        source_path=str(source_path),
        source_sha256=source_sha256(raw),
        parser_version=PARSER_VERSION,
        config={
            **asdict(cfg),
            "config_hash": config_hash(cfg),
        },
        blocks=blocks,
    )


def save_manifest(manifest: BlockManifest, path: Path) -> None:
    path.write_text(json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_manifest(path: Path) -> BlockManifest:
    data = json.loads(path.read_text(encoding="utf-8"))
    return BlockManifest.from_dict(data)


def build_or_load_manifest(source_path: Path, config: ParserConfig | None = None) -> BlockManifest:
    manifest_path = manifest_path_for_source(source_path)
    raw = source_path.read_text(encoding="utf-8", errors="ignore")
    digest = source_sha256(raw)

    if manifest_path.exists():
        manifest = load_manifest(manifest_path)
        if manifest.source_sha256 != digest:
            raise ValueError(
                f"source changed since manifest creation: {source_path}"
            )
        return manifest

    manifest = build_manifest(raw, source_path, config)
    save_manifest(manifest, manifest_path)
    return manifest
