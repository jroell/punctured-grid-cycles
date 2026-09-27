# Hamiltonian cycles with a central hole

This package counts undirected Hamiltonian cycles on a `2n × 2n` grid of lattice vertices after deleting the central `2 × 2` vertices and their incident edges. A cycle is an edge set, without a starting vertex or direction. It also counts geometric orbits under the eight symmetries of the square.

For `n = 8` (the punctured `16 × 16` grid):

- Raw cycles: **1517021583328338160591145724550850**
- Geometric orbits: **189627697916042276889063633686282**
- Peak active states in the full counter: **677909**

The complete table covers `n = 1..10` (sides 2 through 20) and is in [results/sequence.csv](results/sequence.csv). The [research-note draft](output/pdf/punctured-grid-cycles.pdf) gives the recurrence, correctness argument, symmetry reductions, exact symmetry classes, resource measurements, and finite-size comparisons. Its canonical source is [paper/latex/roell-punctured-grids.tex](paper/latex/roell-punctured-grids.tex); [paper/paper.md](paper/paper.md) is a generated text export.

## Build and reproduce

Requirements: a C++17 compiler supporting `unsigned __int128` (Clang or GCC), Make, and Python 3.11+. The counters and checkers have no third-party runtime dependencies. `getrusage` reports peak process RSS on macOS and Linux.

```sh
make all
make benchmark
make test
```

`make benchmark` runs both full counters on every even square size from 2 through 16, with and without the hole, then runs the symmetry reductions. It compares exact counts from both representations. Results are decimal strings in JSON to avoid floating-point rounding. Each full-counter subprocess has a 300-second timeout. The main symmetry benchmark has a 260-second subprocess timeout; the counter itself stops after 1800 seconds or 50 million active states.

Individual runs:

```sh
build/parentheses 16 16 1
build/partners 16 16 1
build/parentheses 16 16 0
build/symmetry 8 half
build/symmetry 8 quarter
```

For the full counters, arguments are `HEIGHT WIDTH HOLE`, with dimensions 1 through 24. `HOLE` is 0 or 1; a punctured board requires even dimensions. For symmetry runs, the first argument is `n`, so the full board has side `2n`. The half-board result reports `rotation = R180` and `reflection = one axial reflection`. The quarter-board result reports `rotation = R90` and `reflection = both axial reflections`.

To rebuild the LaTeX PDF, figures, and source archive (install Tectonic and Pandoc first):

```sh
uv sync --group paper
uv run --group paper python scripts/build_paper.py
```

The document dependencies are pinned in `uv.lock`. The script reads the recorded results and emits the PDF, Markdown export, CSV, two OEIS b-files, figures, source checksums, and `output/arxiv-source.zip`. Edit the canonical LaTeX source for persistent prose changes; edit `scripts/build_assets.py` for figures and tables. Tectonic downloads its TeX bundle on first use.

## What is checked

- Two separately encoded frontier algorithms agree on 40 full-counter runs: ten sizes, two graphs, and two implementations. The original 32 runs and eight extension runs are recorded separately.
- Intact-grid results match OEIS A003763 through `n = 10`.
- Direct DFS enumerates the full cycle sets at punctured sides 4 and 6, then applies all eight square symmetries.
- An independent edge-orbit constraint search verifies half-turn, quarter-turn, axial-reflection, and both-axis fixed counts through punctured side 8. Additional runs verify quarter-turn and both-axis counts at sides 10 and 12; each check has a 60-second limit.
- Burnside integrality, nonnegative integer stabilizer counts, orbit totals, and orbit-size-weighted raw totals are checked at every size.
- Invalid dimensions and mode values are rejected. Addition uses a checked four-limb 256-bit integer; overflow terminates the program.

The two frontier implementations share the integer type and the row-by-row problem decomposition. They are cross-checks, not wholly independent mathematical methods. The Python edge-orbit checker supplies a different enumeration method for the small symmetry cases.

## Files and measurement conventions

- `src/parentheses.cpp`: raw counts with noncrossing parenthesis states.
- `src/partners.cpp`: raw counts with explicit endpoint partners.
- `src/symmetry.cpp`: half-board and quarter-board quotient calculations.
- `scripts/verify.py`: direct cycle DFS and whole-edge-orbit search.
- `results/benchmark.json`: per-run counts, peak state location, elapsed time, and peak RSS.
- `results/symmetry.json`: fixed sets, exact stabilizer classes, and symmetry-run measurements.
- `results/verification.json`: small-case independent checks.
- `results/environment.json`: hardware and compiler metadata.
- `results/frontier-profiles.json`: row-end profiles for the original full-counter runs.
- `results/extension-flat.json`: full-counter runs at sides 18 and 20; adjacent text files hold row profiles.
- `results/symmetry-extension.json`: fixed sets and symmetry classes at n=9 and n=10.
- `results/extension-environment.json`: Boost version, source revisions, limits, and measurement conventions.
- `results/additional-verification.json`: independent quarter-turn and both-axis checks at sides 10 and 12.

A peak state count is the maximum number of distinct states in one active layer, measured after every processed vertex. It is not the sum of the sizes of the two maps held during a transition. RSS includes the whole process and both maps. Timings are single observations on a shared workstation, not repeated isolated benchmarks.

## Interpretation and publication status

The sequence uses `H(1) = 0` for the empty graph. The nontrivial cases begin at `n = 2`.

For `n >= 3`, diagonal reflections fix no Hamiltonian cycle, and the Burnside formula is `(H + R180 + 2*R90 + 2*F)/8`, where `F` refers to one specified axial reflection. Quarter-turn symmetry is impossible when `n` is odd. The `n = 2` graph is a single cycle fixed by every square symmetry.

The finite-size ratios do not prove a limiting growth constant, exponent, or unchanged bulk entropy. A term search returning no OEIS match does not establish novelty. The draft cites the established transfer and symmetry methods used for intact grids. The code and publication package are hosted at [github.com/jroell/punctured-grid-cycles](https://github.com/jroell/punctured-grid-cycles). No arXiv, OEIS, or journal submission has been made.

The [review response](paper/review-response.md) records the mathematical and computational revisions. See [paper/submission-notes.md](paper/submission-notes.md) for the sequence submission text and the remaining publication decisions.

## References

- [OEIS A003763](https://oeis.org/A003763), intact even-square Hamiltonian cycle counts.
- [Ed Wynn, arXiv:1402.0545](https://arxiv.org/abs/1402.0545), symmetry classes of intact square grids.
- [Jesper Lykke Jacobsen, arXiv:0709.2322](https://arxiv.org/abs/0709.2322), Hamiltonian circuits, walks, and chains.
- [Pablo Blanco and Doron Zeilberger, arXiv:2603.24315](https://arxiv.org/abs/2603.24315), rectangular-grid generating functions.

Code is available under the MIT license in [LICENSE](LICENSE).

## Larger-board runs

`python3 scripts/extend.py` runs both full counters serially at sides 18 and 20, intact and punctured. Each process is limited to 1800 seconds and monitored for a 48 GiB RSS ceiling every two seconds. Results are checkpointed in `results/extension.json`; completed cases are reused on rerun. The extension measurements are stored separately from the original n <= 8 benchmarks; the publication build combines completed, checked records into the n <= 10 tables. The shared width cap is 24 because the explicit-partner encoding uses five bits per slot in a 128-bit key. Arithmetic still aborts on 256-bit overflow.

The revised manuscript clarifies the axial-reflection and half-turn proofs, reports intact peak-state counts alongside punctured counts, and plots the log count ratio by parity. Reported third-party verification is not treated as reproduced evidence until its checker sources are available.

For the optional faster backend, install Boost headers (tested with Boost 1.92.0):

```sh
make flat BOOST_CPPFLAGS=-I/opt/homebrew/include  # Homebrew on Apple Silicon
python3 scripts/verify_backends.py
python3 scripts/verify_more_symmetry.py
python3 scripts/extend.py --backend flat
python3 scripts/extend_symmetry.py
python3 scripts/verify_extension.py
```

On systems where Boost is in the compiler's default include path, use `make flat`. The optional backend uses `boost::unordered_flat_map`; it changes state aggregation only. All 46 established raw and symmetry runs are compared against the original backend, including peak-state counts. Extension records identify the backend, and the original standard-library build remains dependency-free. Re-run `extend_symmetry.py` after both raw counters finish to complete the Burnside and stabilizer checks.
