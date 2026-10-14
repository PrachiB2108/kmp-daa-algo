"""Quick demo: run KMP and Boyer-Moore on a toy example and print diagnostics."""
from __future__ import annotations

from boyer_moore import boyer_moore_search
from kmp import kmp_search


def main() -> None:
    text = "ABABDABACDABABCABAB"
    pattern = "ABABCABAB"

    print(f"Text:    {text}")
    print(f"Pattern: {pattern}\n")

    for name, search in (("KMP", kmp_search), ("Boyer-Moore", boyer_moore_search)):
        result = search(text, pattern)
        print(f"-- {name} --")
        print(f"  matches at indices       : {result.matches}")
        print(f"  preprocessing comparisons: {result.preprocessing_comparisons}")
        print(f"  matching comparisons     : {result.matching_comparisons}")
        print(f"  total comparisons        : {result.total_comparisons}")
        print(f"  preprocessing time (us)  : {result.preprocessing_time * 1e6:.2f}")
        print(f"  matching time (us)       : {result.matching_time * 1e6:.2f}")
        print()


if __name__ == "__main__":
    main()
