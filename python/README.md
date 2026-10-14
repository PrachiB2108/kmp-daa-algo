# KMP vs. Boyer-Moore: String Matching & Text Processing

Implementation and empirical analysis of two linear-time substring-search
algorithms:

- **Knuth-Morris-Pratt (KMP)** — preprocesses the pattern into a *Longest
  Prefix-Suffix* (LPS) / failure array, then scans the text once, never
  re-reading a text character after a mismatch.
- **Boyer-Moore (BM)** — preprocesses the pattern into a *bad-character*
  table and a *strong good-suffix* table, then scans the text right-to-left
  within each alignment, often skipping multiple characters per shift.

Both implementations return every match (including overlapping ones) and are
instrumented to count character comparisons and time preprocessing /
matching phases separately.

## Project layout

```
string_matching/
  kmp.py              KMP: compute_lps() + kmp_search()
  boyer_moore.py       Boyer-Moore: bad-char + good-suffix tables + boyer_moore_search()
  text_generator.py    DNA / pseudo-English / uniform-alphabet text generators
  demo.py              Small worked example (textbook pattern) printing diagnostics
  benchmark.py         Full experiment suite -> results/*.csv and results/*.png
  tests/
    test_algorithms.py Correctness tests (vs. str.find) incl. edge cases
  results/             Generated CSVs and plots (created by benchmark.py)
```

## Running it

```powershell
pip install -r requirements.txt
python -m unittest tests.test_algorithms -v   # correctness
python demo.py                                # quick worked example
python benchmark.py                           # full analysis -> results/
```

## Experimental setup

Three experiments, each averaging `REPEATS = 5` random `(text, pattern)`
draws per data point (pattern = a genuine substring of the text, so a match
is always found):

1. **Text length sweep** — pattern length fixed at 12, text length in
   `{1k, 2k, 5k, 10k, 20k, 50k, 100k}` chars, for:
   - **DNA**: alphabet `{A,C,G,T}` (size 4), uniform random.
   - **English prose**: 27-symbol alphabet (26 letters + space) sampled
     using approximate English letter frequencies (pseudo-English, since no
     external corpus is bundled).
2. **Alphabet size sweep** — text length fixed at 20,000, pattern length 12,
   synthetic uniform-random text over alphabets of size
   `{2, 4, 8, 16, 26, 32, 64, 94}`.
3. **Worst-case vs. average-case** — binary alphabet, text length 20,000,
   comparing a random (average-case) pattern against the classic
   `"aaa...ab"` adversarial pattern.

## Results

### Comparisons vs. text length (DNA, alphabet size 4)

![comparisons vs length DNA](../benchmark-data/comparisons_vs_length_DNA.png)

### Comparisons vs. alphabet size (text length 20,000)

![comparisons vs alphabet size](../benchmark-data/comparisons_vs_alphabet_size.png)

(Full plots for English prose and timing are in `../benchmark-data/`: `comparisons_vs_length_English.png`,
`time_vs_length_DNA.png`, `time_vs_length_English.png`, `time_vs_alphabet_size.png`.)

Running `python benchmark.py` from this folder regenerates these into a local `results/` directory.

## Analysis / findings

- **Preprocessing time.** Both are O(m) in the pattern length, so for a
  fixed pattern length (12) preprocessing cost is small and roughly
  constant as text length grows. Boyer-Moore's good-suffix table
  construction does more bookkeeping (two passes, border array) than KMP's
  single-pass LPS, so BM's preprocessing time per run is consistently
  somewhat higher, but it is dwarfed by matching time once the text is more
  than a few hundred characters.

- **Matching-time growth (text length sweep).** Both algorithms scale
  linearly with text length as expected (straight lines in the plots), but
  the **slope differs sharply**: on the 4-symbol DNA alphabet, KMP performs
  roughly **1.24 comparisons per text character** (it is guaranteed
  `<= 2n` comparisons), while Boyer-Moore performs roughly **0.33
  comparisons per text character** here — about 3.7x fewer total
  comparisons at 100,000 characters. This matches the theoretical
  expectation that BM's expected-case behavior is sub-linear in the number
  of text characters actually inspected (it skips characters with the
  bad-character/good-suffix shifts).

- **Effect of alphabet size.** The alphabet-size sweep shows BM's advantage
  grows, then saturates, as the alphabet gets larger: with a binary alphabet
  (size 2) both algorithms must examine most characters (few bad-character
  skips are possible because any character is likely to reoccur nearby), so
  BM's benefit over KMP is modest. As alphabet size increases toward the
  mid-20s–30s (English-like) and beyond, the probability that a text
  character also appears late in the pattern drops sharply, so bad-character
  shifts become large and BM's comparison count drops steeply before
  flattening out for alphabets beyond ~30 symbols (diminishing returns —
  shifts are already close to the maximum possible). KMP is comparison-wise
  almost flat with alphabet size (its guarantee is really about pattern
  self-similarity, not alphabet size), with only a small drop because
  fewer incidental partial matches occur with larger alphabets.

  Practical implication: **DNA sequences (alphabet size 4) are the worst
  case for Boyer-Moore's skip heuristics** among the scenarios tested —
  repeated nucleotides mean more partial matches and smaller shifts — while
  **English prose (alphabet size ~27)** already gives BM a large advantage,
  and purely synthetic large alphabets (size 64–94, e.g., binary/genomic
  encodings with byte-level symbols) give the best case for BM.

- **Worst-case vs. average-case (binary alphabet).** KMP's comparison count
  is nearly identical between average-case and the adversarial
  `"aaa...ab"` pattern (consistent with its `O(n + m)` worst-case
  guarantee — it never regresses). Boyer-Moore's raw comparison count can
  actually *decrease* on this specific adversarial pattern in our runs,
  because the pattern's single trailing mismatch character lets the
  bad-character rule reject most alignments after very few comparisons;
  Boyer-Moore's true theoretical worst case (`O(nm)`) requires patterns
  that are *highly periodic* (e.g., `"aaaa...a"` against a text of all
  `a`s), which the bundled generators do not construct by default — the
  good-suffix rule caps the worst case at `O(n)` even then for the version
  implemented here (strong good suffix), but the plain bad-character-only
  variant can degrade to `O(nm)` on such inputs.

- **Bottom line.** For small, low-entropy alphabets (DNA-like), KMP's
  guarantee of never re-reading text is competitive and BM's advantage is
  smaller; for larger/higher-entropy alphabets (English prose and beyond),
  Boyer-Moore's average-case skip distance makes it substantially faster in
  both comparisons and wall-clock time, which explains why most real-world
  text editors / `grep`-like tools favor Boyer-Moore-family algorithms
  while bioinformatics tools favor KMP/Aho-Corasick-style automata for
  small-alphabet genomic data.

## Complexity summary

| Algorithm    | Preprocessing | Worst-case matching | Typical matching (large alphabet) |
|--------------|---------------|----------------------|------------------------------------|
| KMP          | O(m)          | O(n)                 | O(n)                               |
| Boyer-Moore  | O(m + σ)      | O(n) (strong good suffix) / O(nm) (bad-char only) | O(n/m) best case, sub-linear typical |

where `n` = text length, `m` = pattern length, `σ` = alphabet size.
