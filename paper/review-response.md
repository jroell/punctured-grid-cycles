# Response to the technical review

The canonical manuscript is [the LaTeX source](latex/roell-punctured-grids.tex). Exact terms and run measurements are linked from the [README](../README.md).

1. **OEIS comparison range.** The manuscript specifies the computed range and states that A003763's b-file contains 13 terms. The repository retains an immutable OEIS source-mirror reference and comparison values through n=10.

2. **Axial reflection and half-turn proofs.** The axial-reflection argument now rules out the half-shift: connectivity forces an axis crossing, its edge is fixed setwise, and a half-shift fixes no edge. The half-turn argument states that the center is a lattice face center, so the action fixes neither a vertex nor an edge.

3. **Larger boards.** The shared raw-counter width limit is 24, consistent with the 128-bit explicit-partner encoding. Optional Boost flat hash maps and local partner-field updates make the requested larger computations practical. The standard-library backend remains available. The extension driver checkpoints completed cases and enforces time and memory limits. Separate verification checks agreement between representations, OEIS values, state peaks, Burnside sums, and exact stabilizer identities.

4. **Defect cost.** Section 7 and its plot now emphasize log(H_n/C_n). They distinguish a finite-size log count ratio from a proved limiting free-energy cost and explain the optional mu^4 normalization without asserting an asymptotic theorem.

5. **Parity trend and critical scaling.** The odd log ratios at n=5,7,9 are nearly flat at -3.8764, -3.8727, and -3.8857. The even values approach from above with shrinking drops. The revised discussion says the data are consistent with a common value around -3.88 to -3.89 and labels the geometric-tail estimate near -3.882 as descriptive only. Jacobsen and Kondev's compact-polymer field theory motivates retaining a power-law defect contribution as a possibility. Compact and dense polymers have different universality classes; the text does not assign this hole a scaling operator or exponent.

6. **Intact state counts.** The measurement table includes intact and punctured peak-state columns. The new [frontier-set check](../scripts/verify_frontier_sets.py) compares sorted state keys byte for byte at the first punctured peak position for sides 10, 12, 14, and 16. All four sets equal their intact counterparts at the same scan position, below the hole rows. The [recorded results](../results/frontier-set-verification.json) also check that instrumentation preserves the established counts and peak positions. This explains the equal peaks at those sizes. Set equality at sides 18 and 20 remains untested, and equal keys do not imply equal weights.

7. **Intact parity obstruction.** The text now spells out the complementary case: an intact cycle has length 4n², so its order-four shifts are n² and 3n². For even n these preserve checkerboard color, contradicting the color exchange of the geometric quarter-turn.

Additional independent edge-orbit checks reproduce quarter-turn and both-axis counts at sides 10 and 12. At side 12 these are 8650 and 6406, respectively. The completed checks, search-node counts, and timings are in [additional-verification.json](../results/additional-verification.json). Larger fixed-set counts still rely on the quotient implementation plus algebraic consistency checks. Integrality checks do not supply a false-pass probability without an error model.

The two checker scripts mentioned in the supplied review have not been provided. Their reported results are not counted as reproduced repository evidence.
