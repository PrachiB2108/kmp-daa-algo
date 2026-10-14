"""Correctness tests for KMP and Boyer-Moore against Python's built-in search."""
from __future__ import annotations

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from boyer_moore import boyer_moore_search
from kmp import kmp_search
import text_generator as tg


def naive_matches(text: str, pattern: str) -> list[int]:
    """Reference implementation using Python's str.find (overlapping matches)."""
    matches = []
    start = 0
    while True:
        idx = text.find(pattern, start)
        if idx == -1:
            break
        matches.append(idx)
        start = idx + 1
    return matches


class AlgorithmCorrectnessTests(unittest.TestCase):
    def assert_matches_agree(self, text: str, pattern: str) -> None:
        expected = naive_matches(text, pattern)
        self.assertEqual(kmp_search(text, pattern).matches, expected,
                          msg=f"KMP mismatch for pattern={pattern!r}")
        self.assertEqual(boyer_moore_search(text, pattern).matches, expected,
                          msg=f"Boyer-Moore mismatch for pattern={pattern!r}")

    def test_basic_match(self):
        self.assert_matches_agree("abxabcabcaby", "abcaby")

    def test_no_match(self):
        self.assert_matches_agree("aaaaaaaaaa", "ab")

    def test_overlapping_matches(self):
        self.assert_matches_agree("aaaaaa", "aaa")

    def test_pattern_equals_text(self):
        self.assert_matches_agree("abcdef", "abcdef")

    def test_single_char_pattern(self):
        self.assert_matches_agree("mississippi", "s")

    def test_pattern_longer_than_text(self):
        self.assert_matches_agree("abc", "abcd")

    def test_empty_pattern(self):
        self.assertEqual(kmp_search("abc", "").matches, [])
        self.assertEqual(boyer_moore_search("abc", "").matches, [])

    def test_repetitive_pattern_worst_case(self):
        text = "a" * 500 + "b"
        pattern = tg.worst_case_pattern("ab", 50)
        self.assert_matches_agree(text, pattern)

    def test_dna_random(self):
        text = tg.dna_text(2000, seed=1)
        pattern = tg.extract_pattern(text, 15, seed=2)
        self.assert_matches_agree(text, pattern)

    def test_english_like_random(self):
        text = tg.english_like_text(2000, seed=3)
        pattern = tg.extract_pattern(text, 15, seed=4)
        self.assert_matches_agree(text, pattern)

    def test_uniform_alphabet_random(self):
        rng = random.Random(5)
        for alphabet_size in (2, 10, 50, 94):
            text = tg.uniform_text(alphabet_size, 1500, seed=rng.randint(0, 10_000))
            pattern = tg.extract_pattern(text, 10, seed=rng.randint(0, 10_000))
            self.assert_matches_agree(text, pattern)


if __name__ == "__main__":
    unittest.main()
