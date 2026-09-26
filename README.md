# Hamiltonian cycles with a central hole

This package counts undirected Hamiltonian cycles on a `2n × 2n` grid of lattice vertices after deleting the central `2 × 2` vertices and their incident edges. A cycle is an edge set, without a starting vertex or direction. It also counts geometric orbits under the eight symmetries of the square.

For `n = 8` (the punctured `16 × 16` grid):

- Raw cycles: **1517021583328338160591145724550850**
- Geometric orbits: **189627697916042276889063633686282**
- Peak active states in the full counter: **677909**

The complete table is in [results/sequence.csv](results/sequence.csv). The [research-note draft](output/pdf/punctured-grid-cycles.pdf) gives the recurrence, correctness argument, symmetry reductions, exact symmetry classes, resource measurements, and finite-size comparisons. Its editable text is [paper/paper.md](paper/paper.md); the reproducible document source is [scripts/build_paper.py](scripts/build_paper.py).

## Build and reproduce

Requirements: a C++17 compiler supporting `unsigned __int128` (Clang or GCC), Make, and Python 3.11+. The counters and checkers have no third-party runtime dependencies. `getrusage` reports peak process RSS on macOS and Linux.

```sh
make all
make benchmark
make test
```

`make benchmark` runs both full counters on every even square size from 2 through 16, with and without the hole, then runs the symmetry reductions. It compares exact counts from both representations. Results are decimal strings in JSON to avoid floating-point rounding. Each full-counter subprocess has a 300-second timeout. Symmetry runs have a 240-second internal limit and a three-million-state limit.

Individual runs:

```sh
build/parentheses 16 16 1
build/partners 16 16 1
build/parentheses 16 16 0
build/symmetry 8 half
build/symmetry 8 quarter
```

For the full counters, arguments are `HEIGHT WIDTH HOLE`, with dimensions 1 through 16. `HOLE` is 0 or 1; a punctured board requires even dimensions. For symmetry runs, the first argument is `n`, so the full board has side `2n`. The half-board result reports `rotation = R180` and `reflection = one axial reflection`. The quarter-board result reports `rotation = R90` and `reflection = both axial reflections`.

To rebuild the eight-page PDF and figures:

```sh
uv sync --group paper
uv run --group paper python scripts/build_paper.py
```

The document dependencies are pinned in `uv.lock`. The script reads the recorded results and emits the PDF, Markdown text, CSV, OEIS b-file, figures, and source checksums. Rebuilding the paper overwrites `paper/paper.md`; edit the document source for persistent changes.

## What is checked

- Two separately encoded frontier algorithms agree on all 32 recorded full-counter runs (eight sizes, two graphs, two implementations).
- Intact-grid results match OEIS A003763 through `n = 8`.
- Direct DFS enumerates the full cycle sets at punctured sides 4 and 6, then applies all eight square symmetries.
- An independent edge-orbit constraint search verifies half-turn, quarter-turn, axial-reflection, and both-axis fixed counts through punctured side 8.
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
- `results/frontier-profiles.json`: row-end profiles for all full-counter runs.

A peak state count is the maximum number of distinct states in one active layer, measured after every processed vertex. It is not the sum of the sizes of the two maps held during a transition. RSS includes the whole process and both maps. Timings are single observations on a shared workstation, not repeated isolated benchmarks.

## Interpretation and publication status

The sequence uses `H(1) = 0` for the empty graph. The nontrivial cases begin at `n = 2`.

For `n >= 3`, diagonal reflections fix no Hamiltonian cycle, and the Burnside formula is `(H + R180 + 2*R90 + 2*F)/8`, where `F` refers to one specified axial reflection. Quarter-turn symmetry is impossible when `n` is odd. The `n = 2` graph is a single cycle fixed by every square symmetry.

The finite-size ratios do not prove a limiting growth constant, exponent, or unchanged bulk entropy. A term search returning no OEIS match does not establish novelty. The draft cites the established transfer and symmetry methods used for intact grids. The code and publication package are hosted at [github.com/jroell/punctured-grid-cycles](https://github.com/jroell/punctured-grid-cycles). No arXiv, OEIS, or journal submission has been made.

See [paper/submission-notes.md](paper/submission-notes.md) for the sequence submission text and the remaining publication decisions.

## References

- [OEIS A003763](https://oeis.org/A003763), intact even-square Hamiltonian cycle counts.
- [Ed Wynn, arXiv:1402.0545](https://arxiv.org/abs/1402.0545), symmetry classes of intact square grids.
- [Jesper Lykke Jacobsen, arXiv:0709.2322](https://arxiv.org/abs/0709.2322), Hamiltonian circuits, walks, and chains.
- [Pablo Blanco and Doron Zeilberger, arXiv:2603.24315](https://arxiv.org/abs/2603.24315), rectangular-grid generating functions.

Code is available under the MIT license in [LICENSE](LICENSE).
