# Publication package and submission notes

The package contains a LaTeX research-note draft, exact tables, source code under the MIT license, pinned document dependencies, and independent small-case checks. The public repository is [jroell/punctured-grid-cycles](https://github.com/jroell/punctured-grid-cycles). No arXiv, OEIS, or journal submission has been made.

## Proposed OEIS entries

Two separate entries are prepared:

- [Raw undirected cycle counts](submissions/oeis-raw.md), with b-file `results/oeis-bfile.txt`.
- [Geometric orbits under the square symmetries](submissions/oeis-orbits.md), with b-file `results/oeis-orbits-bfile.txt`.

Both use offset `1,3` and set the empty n=1 case to zero. The manuscript build updates the terms from the verified result files. No A-numbers have been assigned.

The original search for `14,164102,9684216390` returned no result on September 26, 2026; its response is retained in `results/oeis-search.txt`. A separate orbit-term search also returned no match. Search the defining graph as well as the terms before submitting. A negative search does not establish novelty.

## Paper and repository

Repository: [https://github.com/jroell/punctured-grid-cycles](https://github.com/jroell/punctured-grid-cycles). Cite this repository URL when preparing an external submission.

The draft's defensible contributions are the exact punctured-grid table, explicit hole handling, a quarter-turn parity obstruction, reproducible fixed-cycle counts, and exact geometric symmetry classes. Connectivity transfer algorithms and intact-grid symmetry reductions are established work and are cited accordingly.

An arXiv version needs the final author metadata, license selection, and any required endorsement. A journal version needs a targeted novelty check and an assessment of whether this central-hole specialization offers enough content for the venue. Neither arXiv listing nor journal acceptance follows from the size or precision of a count.

The finite-size section is intentionally descriptive. It does not establish that deleting the central block preserves or changes the bulk growth constant, and it does not fit a sub-exponential exponent from this short finite sequence.

## References checked

- OEIS A003763, including comparison terms through n=10: https://oeis.org/A003763
- Ed Wynn, *Enumeration of nonisomorphic Hamiltonian cycles on square grid graphs*, arXiv:1402.0545 (2014): https://arxiv.org/abs/1402.0545. The paper contains the intact-grid symmetry bookkeeping and a quadrant quotient construction.
- Jesper Lykke Jacobsen, *Exact enumeration of Hamiltonian circuits, walks, and chains in two and three dimensions*, arXiv:0709.2322 (2007): https://arxiv.org/abs/0709.2322. The paper discusses exact transfer enumeration and finite-size growth estimates with surface corrections.
- Pablo Blanco and Doron Zeilberger, *Counting (and Randomly Generating) Hamiltonian Cycles in Rectangular Grids*, arXiv:2603.24315 (2026): https://arxiv.org/abs/2603.24315. Metadata and abstract were checked; this is a fixed-width generating-function implementation.

## Revised submission files

The canonical manuscript is `paper/latex/roell-punctured-grids.tex`, using 12pt `amsart`. The build emits `output/pdf/punctured-grid-cycles.pdf` and a source-only `output/arxiv-source.zip`. Separate draft entries are in `paper/submissions/oeis-raw.md` and `paper/submissions/oeis-orbits.md`; arXiv metadata is in `paper/submissions/arxiv-metadata.md`.

Author metadata, account access, license selection, and final submission review remain pending. No external submission has been made. Venue policies must be checked before submission.

## Review revisions

The axial-reflection proof now rules out a half-shift using an axis-crossing edge fixed setwise. The half-turn argument explicitly states the free action on vertices and edges. The finite-size plot shows log(H_n/C_n) by parity, and the metrics table includes intact peak states. The n=9 value reverses the increasing odd-n trend seen over n=3..8. The discussion reports that reversal without asserting a common limit or an unproved gluing theorem. Additional independent edge-orbit checks verify the quarter-turn and both-axis counts at sides 10 and 12.

A supplied review reports additional Python checks. Those are not counted as reproduced repository verification until their source files are available and run here. Congruence checks are necessary consistency checks, not a probabilistic error certificate: a claim of a 1-in-64 false-pass rate requires a specified error model and independence assumptions.
