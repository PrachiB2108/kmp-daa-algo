"""Benchmark harness: compares KMP and Boyer-Moore on comparisons, preprocessing
time, and matching time across alphabet sizes and text lengths (DNA vs. English
prose, plus synthetic uniform alphabets).

Usage:
    python benchmark.py
Outputs CSV + PNG plots under ./results/.
"""
from __future__ import annotations

import csv
import os
import statistics
from dataclasses import asdict, dataclass
from typing import Callable, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import text_generator as tg
from boyer_moore import boyer_moore_search
from kmp import kmp_search

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

ALGORITHMS: Dict[str, Callable] = {
    "KMP": kmp_search,
    "Boyer-Moore": boyer_moore_search,
}

TEXT_LENGTHS = [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000]
ALPHABET_SIZES = [2, 4, 8, 16, 26, 32, 64, 94]
PATTERN_LENGTH = 12
REPEATS = 5  # independent random (text, pattern) draws averaged per data point


@dataclass
class Record:
    algorithm: str
    category: str
    text_length: int
    pattern_length: int
    alphabet_size: int
    preprocessing_comparisons: float
    matching_comparisons: float
    total_comparisons: float
    preprocessing_time_us: float
    matching_time_us: float
    total_time_us: float


def _run_averaged(algorithm_name: str, category: str, alphabet_size: int,
                   text_factory: Callable[[int], str], pattern_length: int,
                   repeats: int = REPEATS) -> Record:
    search_fn = ALGORITHMS[algorithm_name]
    samples = []
    text_length = None
    for seed in range(repeats):
        text = text_factory(seed)
        text_length = len(text)
        pattern = tg.extract_pattern(text, pattern_length, seed=seed + 1000)
        samples.append(search_fn(text, pattern))

    def avg(attr: str) -> float:
        return statistics.mean(getattr(s, attr) for s in samples)

    return Record(
        algorithm=algorithm_name,
        category=category,
        text_length=text_length,
        pattern_length=pattern_length,
        alphabet_size=alphabet_size,
        preprocessing_comparisons=avg("preprocessing_comparisons"),
        matching_comparisons=avg("matching_comparisons"),
        total_comparisons=avg("total_comparisons"),
        preprocessing_time_us=avg("preprocessing_time") * 1e6,
        matching_time_us=avg("matching_time") * 1e6,
        total_time_us=avg("total_time") * 1e6,
    )


def experiment_text_length() -> List[Record]:
    """Fixed pattern length, varying text length, for DNA vs. English-like text."""
    records = []
    factories = {
        "DNA": (lambda length: lambda seed: tg.dna_text(length, seed=seed), 4),
        "English": (lambda length: lambda seed: tg.english_like_text(length, seed=seed), 27),
    }
    for category, (make_factory, alphabet_size) in factories.items():
        for length in TEXT_LENGTHS:
            for algo in ALGORITHMS:
                records.append(_run_averaged(
                    algo, category, alphabet_size, make_factory(length), PATTERN_LENGTH))
    return records


def experiment_alphabet_size() -> List[Record]:
    """Fixed text/pattern length, varying (synthetic uniform) alphabet size."""
    records = []
    fixed_length = 20_000
    for alphabet_size in ALPHABET_SIZES:
        factory = lambda seed, a=alphabet_size: tg.uniform_text(a, fixed_length, seed=seed)
        for algo in ALGORITHMS:
            records.append(_run_averaged(algo, "Uniform", alphabet_size, factory, PATTERN_LENGTH))
    return records


def experiment_worst_case() -> List[Record]:
    """Binary-alphabet worst-case pattern ('aaa...ab') vs. average-case pattern."""
    records = []
    fixed_length = 20_000
    for seed in range(REPEATS):
        text = tg.uniform_text(2, fixed_length, seed=seed)
        avg_pattern = tg.extract_pattern(text, PATTERN_LENGTH, seed=seed + 1000)
        worst_pattern = tg.worst_case_pattern("ab", PATTERN_LENGTH)
        for label, pattern in (("Average-case", avg_pattern), ("Worst-case", worst_pattern)):
            for algo, search_fn in ALGORITHMS.items():
                result = search_fn(text, pattern)
                records.append(Record(
                    algorithm=algo,
                    category=f"Binary-{label}",
                    text_length=fixed_length,
                    pattern_length=PATTERN_LENGTH,
                    alphabet_size=2,
                    preprocessing_comparisons=result.preprocessing_comparisons,
                    matching_comparisons=result.matching_comparisons,
                    total_comparisons=result.total_comparisons,
                    preprocessing_time_us=result.preprocessing_time * 1e6,
                    matching_time_us=result.matching_time * 1e6,
                    total_time_us=result.total_time * 1e6,
                ))
    return records


def write_csv(records: List[Record], filename: str) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(records[0]).keys()))
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))
    return path


def _plot_metric_vs_length(records: List[Record], category: str, metric: str,
                            ylabel: str, filename: str) -> None:
    plt.figure(figsize=(7, 5))
    for algo in ALGORITHMS:
        xs = sorted({r.text_length for r in records if r.category == category and r.algorithm == algo})
        ys = [next(r for r in records if r.category == category and r.algorithm == algo
                   and r.text_length == x).__getattribute__(metric) for x in xs]
        plt.plot(xs, ys, marker="o", label=algo)
    plt.xlabel("Text length (characters)")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs. text length — {category}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, filename), dpi=150)
    plt.close()


def _plot_metric_vs_alphabet(records: List[Record], metric: str, ylabel: str, filename: str) -> None:
    plt.figure(figsize=(7, 5))
    for algo in ALGORITHMS:
        xs = sorted({r.alphabet_size for r in records if r.algorithm == algo})
        ys = [next(r for r in records if r.algorithm == algo and r.alphabet_size == x)
              .__getattribute__(metric) for x in xs]
        plt.plot(xs, ys, marker="o", label=algo)
    plt.xlabel("Alphabet size")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs. alphabet size (text length 20,000)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, filename), dpi=150)
    plt.close()


def main() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    length_records = experiment_text_length()
    alphabet_records = experiment_alphabet_size()
    worst_case_records = experiment_worst_case()

    write_csv(length_records, "text_length_results.csv")
    write_csv(alphabet_records, "alphabet_size_results.csv")
    write_csv(worst_case_records, "worst_case_results.csv")

    for category in ("DNA", "English"):
        _plot_metric_vs_length(length_records, category, "total_comparisons",
                                "Total character comparisons",
                                f"comparisons_vs_length_{category}.png")
        _plot_metric_vs_length(length_records, category, "total_time_us",
                                "Total time (microseconds)",
                                f"time_vs_length_{category}.png")

    _plot_metric_vs_alphabet(alphabet_records, "total_comparisons",
                              "Total character comparisons",
                              "comparisons_vs_alphabet_size.png")
    _plot_metric_vs_alphabet(alphabet_records, "total_time_us",
                              "Total time (microseconds)",
                              "time_vs_alphabet_size.png")

    print(f"Wrote CSVs and plots to {RESULTS_DIR}")
    print("\n=== Worst-case vs. average-case (binary alphabet, text length 20,000) ===")
    for algo in ALGORITHMS:
        for label in ("Average-case", "Worst-case"):
            rows = [r for r in worst_case_records if r.algorithm == algo and r.category == f"Binary-{label}"]
            avg_comparisons = statistics.mean(r.total_comparisons for r in rows)
            print(f"  {algo:12s} {label:13s}: avg total comparisons = {avg_comparisons:,.0f}")


if __name__ == "__main__":
    main()
