"""Synthetic text/pattern generators for benchmarking string-matching algorithms."""
from __future__ import annotations

import random
import string
from typing import List, Optional

DNA_ALPHABET = "ACGT"

# Approximate relative frequencies of letters (+ space) in English prose,
# used to generate pseudo-English text without depending on an external corpus.
_ENGLISH_FREQ = {
    "e": 12.7, "t": 9.1, "a": 8.2, "o": 7.5, "i": 7.0, "n": 6.7, "s": 6.3,
    "h": 6.1, "r": 6.0, "d": 4.3, "l": 4.0, "c": 2.8, "u": 2.8, "m": 2.4,
    "w": 2.4, "f": 2.2, "g": 2.0, "y": 2.0, "p": 1.9, "b": 1.5, "v": 1.0,
    "k": 0.8, "j": 0.15, "x": 0.15, "q": 0.1, "z": 0.07, " ": 18.0,
}
ENGLISH_ALPHABET = "".join(_ENGLISH_FREQ.keys())

# Pool used to synthesize alphabets of arbitrary size (max 94 symbols).
_ALPHABET_POOL = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation


def random_text(alphabet: str, length: int, weights: Optional[List[float]] = None,
                 seed: Optional[int] = None) -> str:
    """Generate ``length`` characters drawn (with replacement) from ``alphabet``."""
    rng = random.Random(seed)
    if weights is None:
        return "".join(rng.choices(alphabet, k=length))
    return "".join(rng.choices(alphabet, weights=weights, k=length))


def dna_text(length: int, seed: Optional[int] = None) -> str:
    """Random DNA sequence over {A, C, G, T} (alphabet size 4)."""
    return random_text(DNA_ALPHABET, length, seed=seed)


def english_like_text(length: int, seed: Optional[int] = None) -> str:
    """Pseudo-English prose sampled from English letter frequencies (alphabet size 27)."""
    letters = list(_ENGLISH_FREQ.keys())
    weights = list(_ENGLISH_FREQ.values())
    return random_text("".join(letters), length, weights=weights, seed=seed)


def uniform_text(alphabet_size: int, length: int, seed: Optional[int] = None) -> str:
    """Uniform random text over a synthetic alphabet of the given size (<= 94)."""
    if not 1 <= alphabet_size <= len(_ALPHABET_POOL):
        raise ValueError(f"alphabet_size must be between 1 and {len(_ALPHABET_POOL)}")
    return random_text(_ALPHABET_POOL[:alphabet_size], length, seed=seed)


def extract_pattern(text: str, pattern_length: int, seed: Optional[int] = None) -> str:
    """Pick a genuine substring of ``text`` so a match is guaranteed (average case)."""
    rng = random.Random(seed)
    start = rng.randint(0, len(text) - pattern_length)
    return text[start:start + pattern_length]


def worst_case_pattern(alphabet: str, pattern_length: int) -> str:
    """Pattern like 'aaa...ab' that stresses the matching phase (e.g. naive/KMP)."""
    if pattern_length <= 1 or len(alphabet) < 2:
        return alphabet[0] * max(pattern_length, 1)
    return alphabet[0] * (pattern_length - 1) + alphabet[1]
