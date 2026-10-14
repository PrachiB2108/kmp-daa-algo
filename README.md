# KMP vs. Boyer–Moore: String Matching & Text Processing

**Project:** Design and Analysis of Algorithms mini project  
**Live site:** <https://prachib2108.github.io/kmp-daa-algo/> (available after GitHub Pages is enabled for this repository)

This project compares two pattern-searching algorithms. Given a text and a
pattern, each algorithm finds every position where the pattern occurs in the
text, including overlapping occurrences.

- **Knuth–Morris–Pratt (KMP)** uses a Longest Prefix-Suffix (LPS) array to
  decide where to continue after a mismatch instead of restarting the search.
- **Boyer–Moore** compares from right to left and uses the bad-character and
  strong good-suffix rules to choose how far to shift the pattern.

The repository contains a browser visualizer and a Python implementation used
for correctness tests and benchmark generation. The browser page runs its own
JavaScript implementations; it does not require a Python server.

## Contents

| Path | Purpose |
|---|---|
| `index.html` | Website layout, interactive visualizer, benchmark charts and complexity summary. |
| `style.css` | Responsive styling and comparison-state colors. |
| `app.js` | JavaScript KMP and Boyer–Moore implementations, animation steps, and UI controls. |
| `benchmark-data/` | Committed benchmark CSV files and chart images displayed on the site. |
| `python/kmp.py` | Python KMP implementation and LPS preprocessing. |
| `python/boyer_moore.py` | Python Boyer–Moore implementation and its preprocessing tables. |
| `python/text_generator.py` | Reproducible DNA-like, English-frequency-like, and uniform random test text. |
| `python/benchmark.py` | Runs benchmark experiments and writes CSV/PNG output to `python/results/`. |
| `python/demo.py` | Small command-line example showing match positions and measured counts/times. |
| `python/tests/test_algorithms.py` | Correctness tests compared with Python's built-in string search. |
| `python/README.md` | Python implementation notes and benchmark discussion. |
| `Explanation.md` | Simple project overview and presentation/run guide for a class demonstration. |

## Run the website

### Option 1: Open it directly

Open `index.html` in a modern browser. No installation or build step is needed.

### Option 2: Serve it locally

From the repository root, run:

```powershell
python -m http.server 8000
```

Then open <http://localhost:8000>. Stop the local server with Ctrl+C in the
terminal.

## Use the visualizer

1. Enter or edit the text and pattern, or choose the Classic, DNA, or English
   prose preset.
2. Use **Step** / **Step Back** to inspect comparisons, **Play** to animate,
   **Pause** to stop, or **Run to end** to finish immediately.
3. Adjust the speed slider to change the animation delay.
4. Compare the two algorithm panels: their current character comparison is
   highlighted green for a match and red for a mismatch. Confirmed matches,
   counts, the KMP LPS array, and Boyer–Moore good-suffix shifts are shown.

The text is horizontally scrollable when it is wider than the panel. The
visualizer rejects an empty pattern and a pattern longer than the text.

## Run the Python implementation

Python 3 is required. From the repository root, run these commands in
PowerShell:

```powershell
cd python
python -m pip install -r requirements.txt
python -m unittest tests.test_algorithms -v
python demo.py
python benchmark.py
```

`requirements.txt` installs Matplotlib for benchmark charts. The algorithm
implementations and correctness tests use the Python standard library. The
benchmark script creates a `python/results/` directory containing its fresh
CSV files and plots. The website displays the committed snapshot in
`benchmark-data/`; regenerating Python results does not automatically replace
that snapshot.

## Benchmark methodology and findings

The benchmark averages five seeded runs per data point. The pattern is chosen
from the generated text, so each ordinary benchmark input contains at least
one occurrence. Pattern length is 12 in the standard sweeps.

1. **Vary text length:** 1,000 to 100,000 characters for uniform DNA text
   (four symbols) and pseudo-English text sampled from approximate letter
   frequencies (26 letters plus space).
2. **Vary alphabet size:** 2, 4, 8, 16, 26, 32, 64, and 94 symbols, with
   text length fixed at 20,000 characters.
3. **Compare binary-pattern inputs:** random patterns selected from binary
   text and a repeated-prefix pattern of the form `aaa...ab`. This is an
   illustrative input comparison, not a proof of Boyer–Moore's theoretical
   worst case.

Both comparison counts and elapsed preprocessing/matching times are recorded.
Times are environment-dependent; comparison counts are more reproducible.
The preprocessing comparison count includes LPS/good-suffix character
comparisons, but does not count table writes or bad-character map construction.

From the committed run, at text length 100,000 with a 12-character pattern:

- For DNA, KMP used about 124,140 matching comparisons (about 1.24 per text
  character); Boyer–Moore used about 32,855 (about 0.33 per text character).
- For pseudo-English, KMP used about 107,516 matching comparisons; Boyer–Moore
  used about 12,443.
- Larger alphabets generally allow Boyer–Moore to skip farther. KMP remains
  linear in text length regardless of alphabet size.

See `benchmark-data/` for the committed plots and raw averages. See
`python/README.md` for additional discussion.

## Complexity

Let $n$ be the text length and $m$ the pattern length.

| Algorithm | Preprocessing | Matching worst case | Typical behavior |
|---|---:|---:|---|
| KMP | $O(m)$ | $O(n)$ | $O(n)$ |
| Boyer–Moore (bad-character + strong good-suffix rules, without Galil optimization) | $O(m)$ for these table constructions | $O(nm)$ in the general worst case | Often sublinear character inspections on larger alphabets; best case can be $O(n/m)$ for a fixed pattern length |

The Boyer–Moore implementation includes both requested shift heuristics but
does not implement the Galil optimization, so it should not be described as
having a guaranteed $O(n)$ matching bound. The benchmark is empirical and
does not establish worst-case complexity.

## Deploy with GitHub Pages

1. Push the repository to GitHub.
2. Open repository **Settings → Pages**.
3. Under **Build and deployment**, select **Deploy from a branch**.
4. Select branch `main` and folder `/(root)`, then save.
5. Once the deployment completes, open the site URL shown on the Pages
   settings page. For this repository, the expected URL is
   <https://prachib2108.github.io/kmp-daa-algo/>.

## Project explanation

For a plain-language explanation, class presentation outline, and step-by-step
run instructions, see [Explanation.md](Explanation.md).
