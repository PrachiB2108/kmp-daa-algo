"""Knuth-Morris-Pratt (KMP) substring search, instrumented for analysis."""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Tuple


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


def compute_lps(pattern: str) -> Tuple[List[int], int]:
    """Build the Longest Prefix-Suffix (failure) array for ``pattern``.

    Returns ``(lps, comparisons)``.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    comparisons = 0
    while i < m:
        comparisons += 1
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps, comparisons


def kmp_search(text: str, pattern: str) -> SearchResult:
    """Find all (possibly overlapping) occurrences of ``pattern`` in ``text``."""
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return SearchResult([], 0, 0, 0.0, 0.0)

    t0 = time.perf_counter()
    lps, pre_comparisons = compute_lps(pattern)
    t1 = time.perf_counter()

    matches: List[int] = []
    comparisons = 0
    i = j = 0
    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                matches.append(i - j)
                j = lps[j - 1]
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1
    t2 = time.perf_counter()

    return SearchResult(
        matches=matches,
        preprocessing_comparisons=pre_comparisons,
        matching_comparisons=comparisons,
        preprocessing_time=t1 - t0,
        matching_time=t2 - t1,
    )
