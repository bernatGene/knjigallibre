from __future__ import annotations


def build_line_starts(raw: str) -> list[int]:
    starts = [0]
    for i, ch in enumerate(raw):
        if ch == "\n":
            starts.append(i + 1)
    return starts


def offset_to_line_col(raw: str, line_starts: list[int], offset: int) -> tuple[int, int]:
    if offset < 0:
        offset = 0
    if offset > len(raw):
        offset = len(raw)

    lo = 0
    hi = len(line_starts) - 1
    line_idx = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if line_starts[mid] <= offset:
            line_idx = mid
            lo = mid + 1
        else:
            hi = mid - 1

    line_start = line_starts[line_idx]
    col = offset - line_start + 1
    return line_idx + 1, col
