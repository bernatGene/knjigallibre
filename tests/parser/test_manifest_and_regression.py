from __future__ import annotations

import json
from pathlib import Path

from knj_parser.block_parser import (
    build_manifest,
    manifest_path_for_source,
    parse_text_to_blocks,
    save_manifest,
    source_sha256,
)
from knj_parser.config import ParserConfig
from knj_parser.models import BlockManifest


def test_manifest_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "book.txt"
    source.write_text("Bonjour le monde.\n\nEncore une phrase.", encoding="utf-8")
    raw = source.read_text(encoding="utf-8")

    manifest = build_manifest(raw, source, ParserConfig(min_words_per_block=1))
    path = manifest_path_for_source(source)
    save_manifest(manifest, path)

    loaded = BlockManifest.from_dict(json.loads(path.read_text(encoding="utf-8")))
    assert loaded.source_sha256 == source_sha256(raw)
    assert len(loaded.blocks) == len(manifest.blocks)
    assert loaded.blocks[0].text == manifest.blocks[0].text


def test_petit_prince_regression_invariants() -> None:
    source = Path("texts/st_exupery_le_petit_prince.txt")
    raw = source.read_text(encoding="utf-8", errors="ignore")
    cfg = ParserConfig(min_words_per_block=1)
    blocks = parse_text_to_blocks(raw, cfg)

    assert blocks
    assert all(block.text.strip() for block in blocks)
    assert all(block.start_offset < block.end_offset for block in blocks)
    assert all(blocks[i].end_offset <= blocks[i + 1].start_offset for i in range(len(blocks) - 1))

    oversized = [b for b in blocks if len(b.text) > cfg.max_block_chars]
    assert len(oversized) / len(blocks) < 0.1

    punctuated = [b for b in blocks if b.text.rstrip()[-1] in ".!?…\"'»"]
    assert len(punctuated) / len(blocks) > 0.70

    joined = "\n".join(block.text for block in blocks)
    assert "S'il vous plaît" in joined or "S’il vous plaît" in joined
