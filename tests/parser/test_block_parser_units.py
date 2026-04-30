from __future__ import annotations

from knj_parser.block_parser import parse_text_to_blocks
from knj_parser.config import ParserConfig


def test_groups_dialogue_lines_when_under_limit() -> None:
    raw = """
    – Bonjour.

    – Salut.

    – Comment vas-tu ?
    """.strip()
    blocks = parse_text_to_blocks(raw, ParserConfig(min_words_per_block=1, max_block_chars=500))
    assert len(blocks) == 1
    assert blocks[0].kind == "dialogue"
    assert "Bonjour" in blocks[0].text
    assert "Salut" in blocks[0].text


def test_splits_long_paragraph_by_sentence() -> None:
    raw = (
        "Première phrase assez longue pour forcer une découpe. "
        "Deuxième phrase aussi assez longue pour dépasser les limites. "
        "Troisième phrase pour compléter le test."
    )
    cfg = ParserConfig(min_words_per_block=1, target_block_chars=40, max_block_chars=60)
    blocks = parse_text_to_blocks(raw, cfg)
    assert len(blocks) >= 2
    assert all(len(block.text) <= 70 for block in blocks)
    assert all(block.text[-1] in ".!?…\"'»" for block in blocks)


def test_keeps_raw_offsets_increasing_without_overlap() -> None:
    raw = "Un paragraphe ici.\n\nUn autre paragraphe là."
    blocks = parse_text_to_blocks(raw, ParserConfig(min_words_per_block=1, max_block_chars=24))
    assert len(blocks) == 2
    assert blocks[0].start_offset < blocks[0].end_offset <= blocks[1].start_offset < blocks[1].end_offset


def test_merges_consecutive_short_blocks_when_under_max() -> None:
    raw = "Un bloc court.\n\nUn autre bloc court."
    cfg = ParserConfig(min_words_per_block=1, max_block_chars=80)
    blocks = parse_text_to_blocks(raw, cfg)
    assert len(blocks) == 1
    assert "Un bloc court." in blocks[0].text
    assert "Un autre bloc court." in blocks[0].text


def test_does_not_merge_blocks_of_different_kinds() -> None:
    raw = "– Bonjour.\n\nTexte narratif assez court."
    cfg = ParserConfig(min_words_per_block=1, max_block_chars=200)
    blocks = parse_text_to_blocks(raw, cfg)
    assert len(blocks) == 2
    assert blocks[0].kind == "dialogue"
    assert blocks[1].kind == "narration"
