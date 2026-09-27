# OEIS submission draft

Status: prepared, not submitted. No A-number assigned.

Name: Number of Hamiltonian cycles up to rotations and reflections in the 2n X 2n square grid graph with its four central vertices deleted.

Data: 0, 1, 3, 20676, 1210546548, 3483478580414922, 145938676601947358766460, 189627697916042276889063633686282, 4450608400247986041886906383605585167240715, 2774300066395485992532938392421228045172137752081602347

Offset: 1,3

Definition: Vertices are (x,y), 1 <= x,y <= 2n, with (n,n), (n,n+1), (n+1,n), (n+1,n+1) deleted. Edges join vertices at Euclidean distance 1. A cycle is an undirected edge set, with no distinguished start or direction. The empty graph at n=1 has count 0 by convention.

Comments: Count orbits of undirected cycle edge sets under the eight symmetries of the square. For n>=3, a(n)=(H_n+R2+2*R4+2*F)/8, where H_n counts raw cycles, R2 and R4 count cycles fixed by the half-turn and quarter-turn, and F counts cycles fixed by one specified axial reflection. Diagonal reflections fix no cycles for n>=3.

Examples: a(2)=1. For n=3, the 14 raw cycles form 3 geometric orbits.

Links: Jason Roell, source code, exact tables, and manuscript, https://github.com/jroell/punctured-grid-cycles

Cross-references: A003763 (intact even-square grids). Add the companion sequence identifier after allocation.

Keywords: nonn,more

Author: Jason Roell

b-file: results/oeis-orbits-bfile.txt
