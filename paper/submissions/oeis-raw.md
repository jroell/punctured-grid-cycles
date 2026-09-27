# OEIS submission draft

Status: prepared, not submitted. No A-number assigned.

Name: Number of undirected Hamiltonian cycles in the 2n X 2n square grid graph with its four central vertices deleted.

Data: 0, 1, 14, 164102, 9684216390, 27867828294632440, 1167509412814480584454378, 1517021583328338160591145724550850, 35604867201983888335090959513825934093936960, 22194400531163887940263507134424320689889325050239815212

Offset: 1,3

Definition: Vertices are (x,y), 1 <= x,y <= 2n, with (n,n), (n,n+1), (n+1,n), (n+1,n+1) deleted. Edges join vertices at Euclidean distance 1. A cycle is an undirected edge set, with no distinguished start or direction. The empty graph at n=1 has count 0 by convention.

Comments: Rotated and reflected cycles are distinct if their edge sets differ. Two frontier implementations agree through n=10.

Examples: a(2)=1: the remaining graph is a single 12-cycle. a(3)=14.

Links: Jason Roell, source code, exact tables, and manuscript, https://github.com/jroell/punctured-grid-cycles

Cross-references: A003763 (intact even-square grids). Add the companion sequence identifier after allocation.

Keywords: nonn,more

Author: Jason Roell

b-file: results/oeis-bfile.txt
