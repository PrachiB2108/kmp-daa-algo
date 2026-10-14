// KMP and Boyer-Moore reimplemented in JS (mirrors the Python reference
// implementation) with per-comparison step recording for visualization.

function computeLPS(pattern) {
  const m = pattern.length;
  const lps = new Array(m).fill(0);
  let length = 0, i = 1, comparisons = 0;
  while (i < m) {
    comparisons++;
    if (pattern[i] === pattern[length]) {
      length++;
      lps[i] = length;
      i++;
    } else if (length !== 0) {
      length = lps[length - 1];
    } else {
      lps[i] = 0;
      i++;
    }
  }
  return { lps, comparisons };
}

function kmpRecordSteps(text, pattern) {
  const n = text.length, m = pattern.length;
  const { lps, comparisons: preComparisons } = computeLPS(pattern);
  const steps = [];
  let i = 0, j = 0;
  while (i < n) {
    const alignment = i - j;
    const matchedIndices = Array.from({ length: j }, (_, k) => k);
    const isMatch = text[i] === pattern[j];
    const step = { i, j, alignment, matchedIndices, isMatch, matched: false, matchIndex: null };
    if (isMatch) {
      i++; j++;
      if (j === m) {
        step.matched = true;
        step.matchIndex = i - j;
        j = lps[j - 1];
      }
    } else if (j !== 0) {
      j = lps[j - 1];
    } else {
      i++;
    }
    steps.push(step);
  }
  return { steps, lps, preComparisons };
}

function buildBadCharTable(pattern) {
  const table = new Map();
  for (let i = 0; i < pattern.length; i++) table.set(pattern[i], i);
  return table;
}

function buildGoodSuffixTable(pattern) {
  const m = pattern.length;
  const shift = new Array(m + 1).fill(0);
  const borderPos = new Array(m + 1).fill(0);
  let comparisons = 0;

  let i = m, j = m + 1;
  borderPos[i] = j;
  while (i > 0) {
    while (j <= m && pattern[i - 1] !== pattern[j - 1]) {
      comparisons++;
      if (shift[j] === 0) shift[j] = j - i;
      j = borderPos[j];
    }
    if (j <= m) comparisons++;
    i--; j--;
    borderPos[i] = j;
  }

  j = borderPos[0];
  for (i = 0; i <= m; i++) {
    if (shift[i] === 0) shift[i] = j;
    if (i === j) j = borderPos[j];
  }

  return { shift, comparisons };
}

function bmRecordSteps(text, pattern) {
  const n = text.length, m = pattern.length;
  const badChar = buildBadCharTable(pattern);
  const { shift: goodSuffix, comparisons: gsComparisons } = buildGoodSuffixTable(pattern);
  const steps = [];
  let s = 0;
  while (s <= n - m) {
    let j = m - 1;
    const matchedIndices = [];
    while (j >= 0) {
      const isMatch = pattern[j] === text[s + j];
      steps.push({ s, j, alignment: s, matchedIndices: matchedIndices.slice(), isMatch, matched: false, matchIndex: null });
      if (!isMatch) break;
      matchedIndices.push(j);
      j--;
    }
    if (j < 0) {
      steps[steps.length - 1].matched = true;
      steps[steps.length - 1].matchIndex = s;
      s += goodSuffix[0];
    } else {
      const badCharShift = j - (badChar.has(text[s + j]) ? badChar.get(text[s + j]) : -1);
      const goodSuffixShift = goodSuffix[j + 1];
      s += Math.max(goodSuffixShift, badCharShift, 1);
    }
  }
  return { steps, badChar, goodSuffix, gsComparisons };
}

// ---------------------------------------------------------------------
// UI wiring
// ---------------------------------------------------------------------

const PRESETS = {
  classic: { text: "ABABDABACDABABCABAB", pattern: "ABABCABAB" },
  dna: {
    text: "ACGTACGTGACTCAGACTGACGTAGCATCAGCATCAGACTACGATCAGCATCAGCATGACGATCAGCATGCAT",
    pattern: "CAGCAT",
  },
  english: {
    text: "she sells seashells by the seashore the shells she sells are surely seashells",
    pattern: "sells",
  },
};

const els = {
  textInput: document.getElementById("textInput"),
  patternInput: document.getElementById("patternInput"),
  errorMsg: document.getElementById("errorMsg"),
  btnReset: document.getElementById("btnReset"),
  btnStepBack: document.getElementById("btnStepBack"),
  btnStepFwd: document.getElementById("btnStepFwd"),
  btnPlayPause: document.getElementById("btnPlayPause"),
  btnRunToEnd: document.getElementById("btnRunToEnd"),
  speedRange: document.getElementById("speedRange"),
  kmpPatternRow: document.getElementById("kmpPatternRow"),
  kmpTextRow: document.getElementById("kmpTextRow"),
  kmpComparisons: document.getElementById("kmpComparisons"),
  kmpPreComparisons: document.getElementById("kmpPreComparisons"),
  kmpMatches: document.getElementById("kmpMatches"),
  kmpLpsTable: document.getElementById("kmpLpsTable"),
  bmPatternRow: document.getElementById("bmPatternRow"),
  bmTextRow: document.getElementById("bmTextRow"),
  bmComparisons: document.getElementById("bmComparisons"),
  bmPreComparisons: document.getElementById("bmPreComparisons"),
  bmMatches: document.getElementById("bmMatches"),
  bmGsTable: document.getElementById("bmGsTable"),
};

const CELL_SIZE = 32;

let state = {
  text: "",
  pattern: "",
  kmp: null,
  bm: null,
  cursor: -1, // shared step cursor (index into the longer step list, scaled per algorithm)
  playing: false,
  timer: null,
};

function buildRun() {
  const text = els.textInput.value;
  const pattern = els.patternInput.value;
  els.errorMsg.textContent = "";

  if (!pattern) {
    els.errorMsg.textContent = "Pattern must not be empty.";
    return false;
  }
  if (pattern.length > text.length) {
    els.errorMsg.textContent = "Pattern is longer than the text.";
    return false;
  }

  state.text = text;
  state.pattern = pattern;
  state.kmp = kmpRecordSteps(text, pattern);
  state.bm = bmRecordSteps(text, pattern);
  state.cursor = -1;
  state.maxSteps = Math.max(state.kmp.steps.length, state.bm.steps.length);

  renderStaticTables();
  renderTextRow("kmp");
  renderTextRow("bm");
  render();
  return true;
}

function renderStaticTables() {
  const { lps } = state.kmp;
  els.kmpLpsTable.textContent =
    "idx : " + [...state.pattern].map((_, i) => String(i).padStart(2)).join(" ") + "\n" +
    "char: " + [...state.pattern].map((c) => c.padStart(2)).join(" ") + "\n" +
    "lps : " + lps.map((v) => String(v).padStart(2)).join(" ");

  const { shift } = state.bm;
  els.bmGsTable.textContent =
    "idx  : " + shift.map((_, i) => String(i).padStart(2)).join(" ") + "\n" +
    "shift: " + shift.map((v) => String(v).padStart(2)).join(" ");
}

function renderTextRow(which) {
  const row = which === "kmp" ? els.kmpTextRow : els.bmTextRow;
  row.innerHTML = "";
  for (const ch of state.text) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.textContent = ch;
    row.appendChild(cell);
  }
}

function renderPatternRow(which, alignment) {
  const row = which === "kmp" ? els.kmpPatternRow : els.bmPatternRow;
  row.innerHTML = "";
  row.style.left = `${alignment * CELL_SIZE}px`;
  for (const ch of state.pattern) {
    const cell = document.createElement("div");
    cell.className = "cell";
    cell.textContent = ch;
    row.appendChild(cell);
  }
}

function clearConfirmed(which) {
  const row = which === "kmp" ? els.kmpTextRow : els.bmTextRow;
  [...row.children].forEach((c) => c.classList.remove("confirmed"));
}

function renderAlgo(which) {
  const run = which === "kmp" ? state.kmp : state.bm;
  const steps = run.steps;
  const idx = Math.min(state.cursor, steps.length - 1);

  const textRow = which === "kmp" ? els.kmpTextRow : els.bmTextRow;
  const comparisonsEl = which === "kmp" ? els.kmpComparisons : els.bmComparisons;
  const preEl = which === "kmp" ? els.kmpPreComparisons : els.bmPreComparisons;
  const matchesEl = which === "kmp" ? els.kmpMatches : els.bmMatches;

  preEl.textContent = which === "kmp" ? run.preComparisons : run.gsComparisons;

  // reset text cell styling
  [...textRow.children].forEach((c) => c.classList.remove("current-match", "current-mismatch", "already-matched"));

  if (idx < 0) {
    renderPatternRow(which, 0);
    comparisonsEl.textContent = "0";
    matchesEl.textContent = "0";
    clearConfirmed(which);
    return;
  }

  const step = steps[idx];
  renderPatternRow(which, step.alignment);

  // mark already-matched + current comparison on both rows
  const patternRow = which === "kmp" ? els.kmpPatternRow : els.bmPatternRow;
  step.matchedIndices.forEach((k) => {
    patternRow.children[k].classList.add("already-matched");
    textRow.children[step.alignment + k].classList.add("already-matched");
  });
  const curClass = step.isMatch ? "current-match" : "current-mismatch";
  patternRow.children[step.j].classList.add(curClass);
  if (textRow.children[step.alignment + step.j]) {
    textRow.children[step.alignment + step.j].classList.add(curClass);
  }

  // confirmed matches accumulated so far
  clearConfirmed(which);
  let matchCount = 0;
  for (let k = 0; k <= idx; k++) {
    if (steps[k].matched) {
      matchCount++;
      for (let p = 0; p < state.pattern.length; p++) {
        if (textRow.children[steps[k].matchIndex + p]) {
          textRow.children[steps[k].matchIndex + p].classList.add("confirmed");
        }
      }
    }
  }

  comparisonsEl.textContent = String(idx + 1);
  matchesEl.textContent = String(matchCount);
}

function render() {
  renderAlgo("kmp");
  renderAlgo("bm");
  const atEnd = state.cursor >= state.maxSteps - 1;
  if (atEnd) stopPlaying();
}

function stepForward() {
  if (state.cursor < state.maxSteps - 1) {
    state.cursor++;
    render();
  } else {
    stopPlaying();
  }
}

function stepBack() {
  if (state.cursor > -1) {
    state.cursor--;
    render();
  }
}

function stopPlaying() {
  state.playing = false;
  els.btnPlayPause.textContent = "▶ Play";
  if (state.timer) {
    clearInterval(state.timer);
    state.timer = null;
  }
}

function startPlaying() {
  if (state.cursor >= state.maxSteps - 1) state.cursor = -1;
  state.playing = true;
  els.btnPlayPause.textContent = "⏸ Pause";
  const tick = () => {
    stepForward();
    if (state.cursor >= state.maxSteps - 1) stopPlaying();
  };
  state.timer = setInterval(tick, Number(els.speedRange.value));
}

els.btnPlayPause.addEventListener("click", () => {
  if (state.playing) stopPlaying();
  else startPlaying();
});
els.btnStepFwd.addEventListener("click", () => { stopPlaying(); stepForward(); });
els.btnStepBack.addEventListener("click", () => { stopPlaying(); stepBack(); });
els.btnReset.addEventListener("click", () => { stopPlaying(); buildRun(); });
els.btnRunToEnd.addEventListener("click", () => {
  stopPlaying();
  state.cursor = state.maxSteps - 1;
  render();
});
els.speedRange.addEventListener("input", () => {
  if (state.playing) { stopPlaying(); startPlaying(); }
});
[els.textInput, els.patternInput].forEach((el) => {
  el.addEventListener("change", () => { stopPlaying(); buildRun(); });
});
document.querySelectorAll("[data-preset]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const preset = PRESETS[btn.dataset.preset];
    els.textInput.value = preset.text;
    els.patternInput.value = preset.pattern;
    stopPlaying();
    buildRun();
  });
});

buildRun();
