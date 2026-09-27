# Response to the technical review

The canonical manuscript is [the LaTeX source](latex/roell-punctured-grids.tex). Exact terms and run measurements are linked from the [README](../README.md).

1. **OEIS comparison range.** The manuscript specifies the computed range and states that A003763's b-file contains 13 terms. The repository retains an immutable OEIS source-mirror reference and comparison values through n=10.

2. **Axial reflection and half-turn proofs.** The axial-reflection argument now rules out the half-shift: connectivity forces an axis crossing, its edge is fixed setwise, and a half-shift fixes no edge. The half-turn argument states that the center is a lattice face center, so the action fixes neither a vertex nor an edge.

3. **Larger boards.** The shared raw-counter width limit is 24, consistent with the 128-bit explicit-partner encoding. Optional Boost flat hash maps and local partner-field updates make the requested larger computations practical. The standard-library backend remains available. The extension driver checkpoints completed cases and enforces time and memory limits. Separate verification checks agreement between representations, OEIS values, state peaks, Burnside sums, and exact stabilizer identities.

4. **Defect cost.** Section 7 and its plot now emphasize log(H_n/C_n). They distinguish a finite-size log count ratio from a proved limiting free-energy cost and explain the optional mu^4 normalization without asserting an asymptotic theorem.

5. **Parity trend.** The n=9 ratio is about 0.020534244, below the n=7 value of about 0.020801394. The additional point reverses the increasing odd-n trend in the original table. The manuscript records this observation and explains why color imbalance alone cannot account for the split: the hole always removes two vertices of each color.

6. **Intact state counts.** The measurement table now includes intact and punctured peak-state columns. It identifies the backend change for the larger runs and cautions against interpreting shared-workstation timings as isolated comparisons.

Additional independent edge-orbit checks reproduce quarter-turn and both-axis counts at sides 10 and 12. At side 12 these are 8650 and 6406, respectively. The completed checks, search-node counts, and timings are in [additional-verification.json](../results/additional-verification.json). Larger fixed-set counts still rely on the quotient implementation plus algebraic consistency checks. Integrality checks do not supply a false-pass probability without an error model.

The two checker scripts mentioned in the supplied review have not been provided. Their reported results are not counted as reproduced repository evidence.
