from __future__ import annotations

from knj_parser.anchors import build_line_starts, offset_to_line_col


def test_offset_to_line_col_handles_unicode_and_newlines() -> None:
    raw = "École\nligne deux\nfin"
    starts = build_line_starts(raw)

    assert offset_to_line_col(raw, starts, 0) == (1, 1)
    assert offset_to_line_col(raw, starts, 6) == (2, 1)
    assert offset_to_line_col(raw, starts, len(raw)) == (3, 4)
