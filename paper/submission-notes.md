# Publication package and submission notes

The local package contains an eight-page research-note draft, exact tables, source code under the MIT license, pinned document dependencies, and independent small-case checks. No external submission or public repository has been created.

## Proposed OEIS entry

**Name:** Number of undirected Hamiltonian cycles in the 2n X 2n square grid graph with its four central vertices deleted.

**Offset:** 1,3

**Data:** 0, 1, 14, 164102, 9684216390, 27867828294632440, 1167509412814480584454378, 1517021583328338160591145724550850

**Definition:** Vertices are the lattice points (x,y), 1 <= x,y <= 2n, excluding (n,n), (n,n+1), (n+1,n), and (n+1,n+1). Edges join points at Euclidean distance 1. Count each Hamiltonian cycle once as an undirected edge set. Rotations and reflections are distinct when they change the edge set. Set a(1)=0 because the graph is empty.

**Examples:** a(2)=1: the remaining graph is a single 12-cycle. a(3)=14; these cycles form three equivalence classes under the eight symmetries of the square.

**Comments:** Two frontier implementations using different connectivity encodings agree through n=8. Each keeps only degree-two partial configurations whose completed components do not close before the final vertex. The implementations use checked 256-bit integer arithmetic.

**Cross-reference:** A003763 counts Hamiltonian cycles on the intact 2n X 2n square grid.

**Keywords:** nonn,more

**Author:** Jason Roell

The b-file is `results/oeis-bfile.txt`. The CSV also contains intact-grid and geometric-orbit counts. The search for `14,164102,9684216390` returned no result on 26 September 2026; its response is retained in `results/oeis-search.txt`. Search the defining graph as well as the terms before submitting. A negative search does not establish novelty.

## Paper and repository

Suggested repository name: `punctured-grid-cycles`. The local Git repository can be published under the intended personal account after that destination is selected. Replace local artifact references with the public repository URL before an external submission.

The draft's defensible contributions are the exact punctured-grid table, explicit hole handling, a quarter-turn parity obstruction, reproducible fixed-cycle counts, and exact geometric symmetry classes. Connectivity transfer algorithms and intact-grid symmetry reductions are established work and are cited accordingly.

An arXiv version needs the final author metadata, license selection, and any required endorsement. A journal version needs a targeted novelty check and an assessment of whether this central-hole specialization offers enough content for the venue. Neither arXiv listing nor journal acceptance follows from the size or precision of a count.

The finite-size section is intentionally descriptive. It does not establish that deleting the central block preserves or changes the bulk growth constant, and it does not fit a sub-exponential exponent from seven nonempty sizes.

## References checked

- OEIS A003763, including all eight intact-grid comparison terms: https://oeis.org/A003763
- Ed Wynn, *Enumeration of nonisomorphic Hamiltonian cycles on square grid graphs*, arXiv:1402.0545 (2014): https://arxiv.org/abs/1402.0545. The paper contains the intact-grid symmetry bookkeeping and a quadrant quotient construction.
- Jesper Lykke Jacobsen, *Exact enumeration of Hamiltonian circuits, walks, and chains in two and three dimensions*, arXiv:0709.2322 (2007): https://arxiv.org/abs/0709.2322. The paper discusses exact transfer enumeration and finite-size growth estimates with surface corrections.
- Pablo Blanco and Doron Zeilberger, *Counting (and Randomly Generating) Hamiltonian Cycles in Rectangular Grids*, arXiv:2603.24315 (2026): https://arxiv.org/abs/2603.24315. Metadata and abstract were checked; this is a fixed-width generating-function implementation.
