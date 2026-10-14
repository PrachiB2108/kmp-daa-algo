"""Boyer-Moore substring search using the bad-character and strong
good-suffix heuristics (Gusfield's two-pass good-suffix construction),
instrumented for analysis.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class SearchResult:
    matches: List[int]
    preprocessing_comparisons: int
    matching_comparisons: int
    preprocessing_time: float
    matching_time: float

    @property
    def total_comparisons(self) -> int:
        return self.preprocessing_comparisons + self.matching_comparisons

    @property
    def total_time(self) -> float:
        return self.preprocessing_time + self.matching_time


def build_bad_character_table(pattern: str) -> Dict[str, int]:
    """Map each character to its last index in ``pattern`` (bad-character rule)."""
    table: Dict[str, int] = {}
    for i, ch in enumerate(pattern):
        table[ch] = i
    return table


def build_good_suffix_table(pattern: str) -> Tuple[List[int], int]:
    """Strong good-suffix shift table (size ``m + 1``).

    Returns ``(shift, comparisons)``.
    """
    m = len(pattern)
    shift = [0] * (m + 1)
    border_pos = [0] * (m + 1)
    comparisons = 0

    # Case 1: matching suffixes that also occur elsewhere in the pattern.
    i, j = m, m + 1
    border_pos[i] = j
    while i > 0:
        while j <= m and pattern[i - 1] != pattern[j - 1]:
            comparisons += 1
            if shift[j] == 0:
                shift[j] = j - i
            j = border_pos[j]
        if j <= m:
            comparisons += 1
        i -= 1
        j -= 1
        border_pos[i] = j

    # Case 2: widest border of the whole pattern, for prefixes with no match.
    j = border_pos[0]
    for i in range(m + 1):
        if shift[i] == 0:
            shift[i] = j
        if i == j:
            j = border_pos[j]

    return shift, comparisons


def boyer_moore_search(text: str, pattern: str) -> SearchResult:
    """Find all occurrences of ``pattern`` in ``text`` using Boyer-Moore."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return SearchResult([], 0, 0, 0.0, 0.0)

    t0 = time.perf_counter()
    bad_char = build_bad_character_table(pattern)
    good_suffix, gs_comparisons = build_good_suffix_table(pattern)
    t1 = time.perf_counter()

    matches: List[int] = []
    comparisons = 0
    s = 0  # current alignment of pattern[0] against text[s]
    while s <= n - m:
        j = m - 1
        while j >= 0:
            comparisons += 1
            if pattern[j] != text[s + j]:
                break
            j -= 1
        if j < 0:
            matches.append(s)
            s += good_suffix[0]
        else:
            bad_char_shift = j - bad_char.get(text[s + j], -1)
            s += max(good_suffix[j + 1], bad_char_shift, 1)
    t2 = time.perf_counter()

    return SearchResult(
        matches=matches,
        preprocessing_comparisons=gs_comparisons,
        matching_comparisons=comparisons,
        preprocessing_time=t1 - t0,
        matching_time=t2 - t1,
    )
