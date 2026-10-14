# KMP vs. Boyer-Moore — String Matching & Text Processing

**Live demo:** https://PrachiB2108.github.io/kmp-daa-algo/ *(enable GitHub Pages in repo Settings to activate — see below)*

A Design & Analysis of Algorithms mini project implementing and comparing two
linear-time substring-search algorithms:

- **Knuth-Morris-Pratt (KMP)** — preprocesses the pattern into a Longest
  Prefix-Suffix (LPS) failure array, then scans the text once without ever
  re-reading a character.
- **Boyer-Moore (BM)** — preprocesses a bad-character table and a strong
  good-suffix table, then scans each alignment right-to-left, skipping
  multiple characters per shift.

## What's in this repo

| Path | Description |
|---|---|
| `index.html`, `style.css`, `app.js` | Static website: step-by-step visualizer (both algorithms run side-by-side, highlighting every comparison) + embedded benchmark charts. Pure HTML/CSS/JS, no build step — deployable directly with GitHub Pages. |
| `benchmark-data/` | CSV results and PNG charts produced by the Python benchmark (comparisons/time vs. text length and alphabet size). |
| `python/` | Original Python reference implementation (`kmp.py`, `boyer_moore.py`, `text_generator.py`, `benchmark.py`, `demo.py`) + unit tests. This is what generated `benchmark-data/`. |

## Running the website locally

Just open `index.html` in a browser — it has no dependencies or build step.
Or serve it locally:

```powershell
python -m http.server 8000
# then open http://localhost:8000
```

## Running the Python reference implementation

```powershell
cd python
pip install -r requirements.txt
python -m unittest tests.test_algorithms -v   # correctness tests
python demo.py                                # worked example
python benchmark.py                           # regenerate benchmark-data/
```

## Deploying with GitHub Pages

1. Push this repo to GitHub.
2. In the repo on GitHub: **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Branch: `main`, folder: `/ (root)`. Save.
5. GitHub publishes the site at `https://<your-username>.github.io/<repo-name>/`
   within a minute or two.

## Key findings (full analysis in `python/README.md`)

- On 100,000 characters of DNA text (alphabet size 4), KMP performs
  ≈1.24 comparisons/char vs. Boyer-Moore's ≈0.33 — ~3.7× fewer for BM.
- On English-like prose (larger alphabet), Boyer-Moore's advantage widens
  further (≈0.12 comparisons/char).
- KMP's comparison count is nearly flat across alphabet sizes; Boyer-Moore
  improves sharply as alphabet size grows, then plateaus past ~30 symbols.
- KMP's worst-case comparisons barely change on an adversarial pattern,
  confirming its true `O(n)` guarantee.

## Complexity

| Algorithm | Preprocessing | Worst-case matching | Typical (large alphabet) |
|---|---|---|---|
| KMP | O(m) | O(n) | O(n) |
| Boyer-Moore | O(m + σ) | O(n) with strong good suffix | O(n/m) best case, sub-linear typical |

n = text length, m = pattern length, σ = alphabet size.
