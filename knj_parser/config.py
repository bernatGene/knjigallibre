from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParserConfig:
    min_words_per_block: int = 3
    target_block_chars: int = 420
    max_block_chars: int = 620
    group_dialogue: bool = True
    split_long_paragraphs: bool = True
    merge_hyphenated_linebreaks: bool = True
    drop_control_lines: bool = True

    # Keep these simple and explicit for maintainability.
    control_line_patterns: tuple[str, ...] = (
        r"^\s*[-–—]?\s*\d+\s*[-–—]?\s*$",
        r"^\s*table des matières\s*$",
        r"^\s*chapitre\s+[ivxlcdm0-9]+\b.*$",
        r"^\s*premier chapitre\b.*$",
        r"^\s*à propos de cette édition électronique\b.*$",
        r"^\s*édition du groupe.*$",
        r"^\s*\d{4}\s*$",
        r"^\s*antoine de saint-exupéry\s*$",
        r"^\s*le petit prince\s*$",
    )
