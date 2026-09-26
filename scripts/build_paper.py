#!/usr/bin/env python3
"""Build the research note and figures from the recorded exact results."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
FIG=ROOT/'paper/figures';FIG.mkdir(parents=True,exist_ok=True)
rows=json.loads((ROOT/'results/benchmark.json').read_text())
base={r['width']//2:r for r in rows if r['engine']=='parentheses' and r['hole']}
intact={r['width']//2:r for r in rows if r['engine']=='parentheses' and not r['hole']}
sym={r['n']:r for r in json.loads((ROOT/'results/symmetry.json').read_text())}
verification=json.loads((ROOT/'results/verification.json').read_text())
assert set(base)==set(range(1,9)) and set(sym)==set(range(2,9))
assert any(r['method']=='edge-orbit search' and r['side']==8 for r in verification)
for n in base:
    matches=[r['count'] for r in rows if r['width']==2*n and r['hole']]
    assert len(matches)==2 and matches[0]==matches[1]
H={n:int(r['count']) for n,r in base.items()}
C={n:int(r['count']) for n,r in intact.items()}
fmt=lambda x:f'{int(x):,}'

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':180})
fig,axs=plt.subplots(1,2,figsize=(7.0,2.6),gridspec_kw={'width_ratios':[1,1.8]})
ax=axs[0];side=8;n=4
present={(x,y) for x in range(1,side+1) for y in range(1,side+1) if not(x in (n,n+1) and y in (n,n+1))}
for x,y in present:
    for p in ((x+1,y),(x,y+1)):
        if p in present:ax.plot([x,p[0]],[y,p[1]],color='#b8bcc6',lw=.7)
ax.scatter(*zip(*sorted(present)),s=9,color='#29334a',zorder=3)
ax.scatter([4,4,5,5],[4,5,4,5],marker='x',s=36,color='#b43831',zorder=4)
ax.set(aspect='equal',xlim=(.5,8.5),ylim=(8.5,.5),title='8 × 8 example')
ax.axis('off')
for hole,label,color in [(False,'Intact','#737b8c'),(True,'Central hole','#6844a5')]:
    text=json.loads((ROOT/'results/frontier-profiles.json').read_text())[f'parentheses-16-{int(hole)}']
    points=[(int(a),int(b)) for a,b in re.findall(r'row (\d+): (\d+) states',text)]
    ax=axs[1];ax.plot(*zip(*points),marker='o',ms=3,label=label,color=color)
ax.set(xlabel='Completed row (16 × 16)',ylabel='Active states after row',xticks=[1,4,7,8,9,12,16])
ax.axvspan(7.5,9.5,color='#eee7f5',zorder=-1)
ax.legend(frameon=False,fontsize=9);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
fig.tight_layout();fig.savefig(FIG/'hole-and-states.png');fig.savefig(FIG/'hole-and-states.pdf');plt.close(fig)

fig,ax=plt.subplots(figsize=(4.6,2.8));n=4
present={(x,y) for x in range(1,n+1) for y in range(1,n+1) if (x,y)!=(n,n)}
for x,y in present:
    for p in ((x+1,y),(x,y+1)):
        if p in present:ax.plot([x,p[0]],[y,p[1]],color='#6a7488',lw=1)
ax.scatter(*zip(*present),s=18,color='#29334a',zorder=3)
for k in range(1,n):
    outer=5.2+(n-1-k)*.4
    verts=[(n,k),(outer,k),(outer,outer),(k,outer),(k,n)]
    # Two quadratic segments place the seam edge outside the quadrant.
    path=PlotPath(verts,[PlotPath.MOVETO,PlotPath.CURVE3,PlotPath.CURVE3,PlotPath.CURVE3,PlotPath.CURVE3])
    ax.add_patch(PathPatch(path,fill=False,color='#6844a5',lw=1.4,ls='--'))
ax.scatter([n],[n],marker='x',color='#b43831',s=45)
ax.set(xlim=(.4,6.6),ylim=(6.6,.4),aspect='equal');ax.axis('off')
ax.text(.8,.4,'Quarter board: 4 × 4 minus one corner',fontsize=10)
fig.tight_layout();fig.savefig(FIG/'quarter-quotient.png');fig.savefig(FIG/'quarter-quotient.pdf');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(7,2.55))
ns=list(range(3,9))
for parity,label,marker in [(0,'n even','o'),(1,'n odd','s')]:
    xs=[n for n in ns if n%2==parity]
    axs[0].plot([2*n for n in xs],[H[n]/C[n] for n in xs],marker=marker,label=label)
axs[0].set(xlabel='Side length 2n',ylabel='Punctured / intact count',xticks=[6,8,10,12,14,16]);axs[0].legend(frameon=False,fontsize=9)
axs[1].plot([2*n for n in ns],[math.exp(math.log(C[n])/(4*n*n)) for n in ns],marker='o',label='Intact',color='#737b8c')
axs[1].plot([2*n for n in ns],[math.exp(math.log(H[n])/(4*n*n-4)) for n in ns],marker='o',label='Punctured',color='#6844a5')
axs[1].set(xlabel='Side length 2n',ylabel='Per-vertex growth estimate',xticks=[6,8,10,12,14,16]);axs[1].legend(frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(FIG/'finite-size.png');fig.savefig(FIG/'finite-size.pdf');plt.close(fig)

for name,family in [('Body','DejaVu Serif'),('Sans','DejaVu Sans'),('Mono','DejaVu Sans Mono')]:
    pdfmetrics.registerFont(TTFont(name,font_manager.findfont(family)))
pdfmetrics.registerFont(TTFont('SansBold',font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'))))
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9.6,leading=13.6,spaceAfter=8),
 'h1':ParagraphStyle('h1',fontName='SansBold',fontSize=15,leading=19,spaceAfter=13),
 'h2':ParagraphStyle('h2',fontName='SansBold',fontSize=11,leading=14,spaceBefore=7,spaceAfter=6),
 'title':ParagraphStyle('title',fontName='SansBold',fontSize=20,leading=25,spaceAfter=13),
 'caption':ParagraphStyle('caption',fontName='Sans',fontSize=8.0,leading=11,spaceAfter=9),
 'math':ParagraphStyle('math',fontName='Sans',fontSize=10,leading=15,spaceBefore=3,spaceAfter=10,leftIndent=12),
 'table':ParagraphStyle('table',fontName='Sans',fontSize=8.2,leading=11),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=8.0,leading=11,spaceAfter=7),
}
story=[];md=[]
def p(text,kind='body'):
    text=text.replace('\u2019', chr(39))
    story.append(Paragraph(escape(text).replace('\n','<br/>'),styles[kind]));md.append(text+'\n')
def heading(text,level=1):
    story.append(Paragraph(escape(text),styles['h1' if level==1 else 'h2']));md.append('#'*level+' '+text+'\n')
def page():story.append(PageBreak());md.append('\n<!-- page -->\n')
def table(headers,data,widths):
    cells=[[Paragraph(escape(str(x)),styles['table']) for x in headers]]
    cells += [[Paragraph(escape(str(x)),styles['table']) for x in row] for row in data]
    t=Table(cells,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eceef3')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#aeb4bf')),('LINEBELOW',(0,-1),(-1,-1),.6,colors.HexColor('#aeb4bf'))]))
    story.extend([t,Spacer(1,10)])
    md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in data)+'\n')
def figure(name,width,height,caption):
    story.append(Image(str(FIG/name),width=width,height=height));p(caption,'caption');md.append(f'![{caption}](figures/{name})\n')

p('Hamiltonian cycles on square grids\nwith a central 2 × 2 hole','title')
p('Jason Roell  •  Research-note draft  •  26 September 2026','small')
heading('Abstract',2)
p('I enumerate undirected Hamiltonian cycles on the 2n × 2n lattice grid after deleting its four central vertices, for 1 ≤ n ≤ 8. Two frontier implementations give identical exact counts. Half-board and quarter-board reductions also count cycles fixed by square symmetries, giving geometric orbit counts and exact stabilizer classes. A separate edge-orbit search verifies the symmetry counts through the 8 × 8 case. The note includes state counts, resource measurements, and reproducible source code. Its finite-size comparisons are descriptive; they do not establish a limiting growth constant or a new critical exponent.')
heading('1. Definition and exact sequence',2)
p('Let Gₙ have vertices (x, y) with 1 ≤ x, y ≤ 2n, except for (n, n), (n, n+1), (n+1, n), and (n+1, n+1). Edges join lattice neighbors. For n ≥ 2 it has 4n² − 4 vertices and 8n² − 4n − 12 edges. Let Hₙ count connected spanning subgraphs in which every vertex has degree two. Cycles are edge sets: no starting vertex or direction is distinguished. Rotated and reflected edge sets are initially distinct. Set H₁ = 0 because G₁ is empty.')
table(['n','Grid','Hₙ'],[[n,f'{2*n} × {2*n}',str(H[n])] for n in range(1,9)],[28,66,410])
p('The 4 × 4 punctured graph is a single 12-cycle. At the largest size the raw count is '+fmt(H[8])+', while the count modulo all eight symmetries of the square is '+fmt(sym[8]['orbits'])+'.')
p('The enumeration method is an adaptation of established connectivity transfer methods, not a claim of a new general algorithm. Related work and the present verification boundary are discussed in Section 8.','small')
page()
heading('2. Frontier recurrence and correctness')
p('Process lattice positions in row-major order. A frontier separates processed positions from unprocessed positions and has at most w+1 slots for a board of width w. A slot is empty or carries a selected edge to the unprocessed side. Every processed vertex has its required degree, and every connected component built so far is a path. The state records which occupied slots are the two ends of each such path.')
p('In the primary implementation, planarity makes the endpoint pairing noncrossing. Encode empty slots by 0 and the two ends of each pair by opening and closing parentheses, represented by 1 and 2. A word of w+1 slots uses 2(w+1) bits. The checker stores each partner index explicitly; it does not use parenthesis matching. Both implementations aggregate equal frontier states in hash maps.')
p('Empty slots and noncrossing endpoint pairs form Motzkin words. Consequently, w+1 slots admit at most M(w+1) possible words, where M is the Motzkin sequence. At width 16 this bound is M(17) = 2,356,779. Only reachable states are created. A local update has at most two choices; matching a parenthesis can scan O(w) slots.')
heading('Local transitions',2)
table(['Incoming selected edges','Required action'],[
 ['0','Choose both outgoing edges, right and down, if both neighbors exist. Create a new paired path.'],
 ['1','Choose exactly one available outgoing edge and move the incoming path endpoint to it.'],
 ['2, different paths','Choose no outgoing edge. Join the two paths and pair their other endpoints.'],
 ['2, same path','Accept only at the last remaining vertex, with no other occupied frontier slots.'],
 ['Deleted position','Permit no selected incident edges. Pass the state through only when both local slots are empty.']],[133,371])
p('If Dₜ(s) is the number of partial edge sets producing state s after t positions, then Dₜ₊₁(s′) is the sum of Dₜ(s) over legal local choices leading from s to s′. Initialize the empty state with weight one. At each row boundary, shift the contour slots; at the final vertex, accumulate only the legal single-cycle closure.')
heading('Correctness argument',2)
p('Induct on the processing order. Every legal transition preserves degree two at a newly processed vertex and preserves the path interpretation of the frontier. Joining two ends of the same path is the only way to create a closed component; rejecting that transition before the final closure excludes every disconnected 2-factor. Conversely, restricting any Hamiltonian cycle to successive processed regions produces exactly these legal states and choices. Each lattice edge is decided once, at its earlier endpoint, so an accepted edge set has exactly one construction history. No division by the cycle length or by two is required.')
p('Counters are checked unsigned 256-bit integers, implemented as four 64-bit limbs. Addition aborts on overflow instead of wrapping. No overflow occurred in any recorded run. The implementations accept dimensions up to 16, so their state encodings remain within the supported bit widths.','small')
page()
heading('3. The hole, pruning, and measured state space')
p('A removed vertex contributes only an empty local transition. Edges pointing into the hole are disabled before they can be selected. The geometric scan still crosses the entire rectangular board. Empty slots at the hole do not split the state into independent left and right problems: paths on opposite sides can already be connected through the processed region, and their endpoint pairing must be retained globally.')
p('The hole creates an inner face, but it does not invalidate noncrossing pairings on the outer scan contour. Disjoint planar paths with endpoints on that contour cannot realize an interlacing pairing. No extra winding label is needed for the raw count; the state already retains exactly the connectivity that can affect a continuation.')
figure('hole-and-states.png',504,187,'Figure 1. Deleted vertices (crosses) and the row-end state profile for side 16. Shading marks the rows containing deleted vertices. The reduction starts one row earlier because edges into the hole are disabled. The chart is sampled at row ends; the peak over every vertex transition is larger.')
table(['Grid','Peak states','Time (s)','Peak RSS (MiB)'],[[f'{2*n} × {2*n}',fmt(base[n]['peak_states']),f"{base[n]['seconds']:.6f}",f"{base[n]['max_rss_mib']:.3f}"] for n in range(2,9)],[85,125,130,164])
p(f"For the 16 × 16 punctured board, the peak of {fmt(base[8]['peak_states'])} distinct active states first occurs after row {base[8]['peak_row']}, column {base[8]['peak_col']}. At row ends, the maximum is 349,998 states. The two hash maps coexist during a transition; the reported process RSS includes both maps, buckets, and allocator overhead.")
p('Pruning consists of degree constraints, missing-neighbor constraints, and rejection of premature cycles. The raw counter does not identify reflection-related or rotation-related states, and it does not perform future-reachability pruning. Measurements are single runs on an Apple M4 Max with 128 GiB RAM, using Apple clang 21.0.0 and -O3 -std=c++17. They are not repeated or isolated performance benchmarks.','small')
page()
heading('4. Counting fixed cycles on smaller boards')
p('Write R₂ for the number of full-board cycles fixed by 180° rotation, R₄ for the number fixed by 90° rotation, F for those fixed by one specified horizontal or vertical reflection, and B for those fixed by both of those reflections. The symmetry counter uses explicit endpoint partners and allows temporary boundary stubs. It never closes a path inside the smaller board.')
heading('Half board: F and R₂',2)
p('Take rows 1 through n, with the two central vertices removed from the last row. A reflection-fixed spanning cycle must cross the reflection axis. Each crossing edge is fixed setwise, and a nonidentity reflection of a cycle can fix only two edges when it fixes no vertices. Thus there are exactly two crossings. The retained half is a single Hamiltonian path whose two endpoints lie at allowed positions on the cut. Counting final states with exactly two paired stubs gives F.')
p('For a half-turn, identify every omitted vertex with its rotated representative. On the cut, pair column x with column 2n+1−x. Selected seam edges complete the half-board paths into a quotient cycle. Require one quotient component and an odd number of seam edges. Each seam changes the copy index by one modulo two; odd parity makes the lift one full-board cycle rather than two cycles. This gives R₂ without enumerating full-board cycles.')
heading('Quarter board: R₄ and B',2)
p('For a quarter-turn, use the n × n quadrant with corner (n, n) deleted. Add seam edges joining (n, k) to (k, n), for 1 ≤ k < n. A connected quotient cycle lifts to a connected cycle on four copies precisely when its net change of copy index is coprime to four. Each seam contributes +1 or −1, so this condition is equivalent to an odd number of seam edges. Final states are tested for this parity and for a single quotient component.')
figure('quarter-quotient.png',322,196,'Figure 2. Quarter-board quotient for the 8 × 8 case. Dashed curves are the additional seam edges, not original grid edges. The deleted corner removes the central obstruction.')
p('If a full cycle is fixed by both axial reflections, it crosses each axis exactly twice. Cutting at those four edges leaves one spanning path in each quadrant. Its endpoints lie respectively on the two inner sides. Counting quarter-board states with exactly two paired stubs, one on each inner side, gives B. Reflection reconstructs the full cycle uniquely.')
page()
heading('5. Burnside count and parity restrictions')
p('For n ≥ 3, a diagonal reflection fixes 2n−2 remaining vertices of Gₙ. Its restriction to a Hamiltonian cycle would be a nonidentity cycle automorphism fixing at least four vertices, which is impossible. Thus neither diagonal reflection fixes a cycle. The n=2 graph is the single 12-cycle and is fixed by every square symmetry.')
p('A quarter-turn exchanges the two checkerboard colors of an even-sided grid. On a Hamiltonian cycle of length 4n²−4, an order-four rotation acts by a shift of n²−1 or 3(n²−1) vertices. When n is odd these shifts are even, so they preserve checkerboard color. This contradiction proves R₄ = 0 for odd n. The deleted central block reverses the familiar parity obstruction for intact square grids [2].')
p('Let Oₙ count edge sets modulo the dihedral group D₄. Burnside’s lemma gives, for n ≥ 3:','body')
p('Oₙ = (Hₙ + R₂ + 2R₄ + 2F) / 8.','math')
p('The identity contributes Hₙ; the half-turn contributes R₂; the two quarter-turns have the same fixed set; and the two axial reflections are conjugate. For n=2, add the two diagonal-reflection contributions of one before dividing by eight.')
table(['n','R₂: 180° rotation','F: one axial reflection'],[[n,str(sym[n]['r180']),str(sym[n]['axis'])] for n in range(2,9)],[28,238,238])
table(['n','R₄: 90° rotation','B: both axes','Oₙ: geometric orbits'],[[n,str(sym[n]['r90']),str(sym[n]['both_axes']),str(sym[n]['orbits'])] for n in range(2,9)],[25,91,78,310])
p('In particular, O₈ = '+fmt(sym[8]['orbits'])+'. These are geometric equivalence classes under the symmetries of the embedded square, not classes under arbitrary abstract graph isomorphism.')
p('For every size, the Burnside numerator is divisible by eight. That is a consistency check, not an independent proof of the fixed-cycle counts. The separate edge-orbit enumeration in Section 8 supplies a different check.','small')
page()
heading('6. Exact stabilizer classes')
p('Burnside gives the total number of orbits. The same fixed-set counts determine how many orbits have each exact symmetry group. For n ≥ 3, diagonal reflections are absent. A cycle cannot simultaneously have quarter-turn and axial-reflection symmetry, since those symmetries would generate a diagonal reflection. The remaining possibilities are the five rows below.')
table(['Exact stabilizer','Orbit size','Number of orbits'],[
 ['Identity only','8','(Hₙ − R₂ − 2F + 2B) / 8'],
 ['One axial reflection','4','(F − B) / 2'],
 ['180° rotation only','4','(R₂ − R₄ − B) / 4'],
 ['Both axial reflections and 180°','2','B / 2'],
 ['90° rotations, no reflection','2','R₄ / 2']],[228,62,214])
p('To derive the formulas, first observe that B and R₄ count disjoint sets of edge sets with order-four stabilizers. Each such orbit has two members. After subtracting them from R₂, the remaining half-turn-fixed edge sets come in orbits of size four. Each one-reflection orbit contributes two members fixed by the specified axis, which explains the factor two in (F−B)/2. Subtracting all nontrivial stabilizers from Hₙ gives the first row.')
heading('The 16 × 16 punctured board',2)
classes=sym[8]['classes']
table(['Exact symmetry','Number of geometric orbits'],[
 ['Identity only',str(classes['trivial'])],
 ['One axial reflection',str(classes['one_axis'])],
 ['180° rotation only',str(classes['half_turn_only'])],
 ['Both axes and 180° rotation',str(classes['both_axes'])],
 ['90° rotations, no reflection',str(classes['quarter_turn'])],
 ['All square symmetries','0'],
 ['Total',str(sym[8]['orbits'])]],[205,299])
p('The class counts are all nonnegative integers. Their sum equals O₈. Weighting them by orbit sizes 8, 4, 4, 2, and 2 recovers H₈ exactly. The same checks pass for every computed size. For n=2, there is instead one orbit with full D₄ stabilizer and orbit size one.')
p('This class decomposition follows the same group-action bookkeeping used for intact grids by Wynn [2]. The half-board and quarter-board domains differ here because the central vertices are absent. The explicit quotient connectivity and seam-parity tests prevent counting a symmetric union of several cycles as one Hamiltonian cycle.')
page()
heading('7. Finite-size comparison with intact grids')
p('Let Cₙ count undirected Hamiltonian cycles on the intact 2n × 2n grid, as in OEIS A003763 [1]. Both implementations reproduce all eight available comparison values used here. Define the same-footprint ratio Qₙ = Hₙ/Cₙ. This ratio is not a probability of surviving vertex deletion: deleting vertices from an intact Hamiltonian cycle generally does not leave a Hamiltonian cycle.')
p('For a comparison normalized by the number of visited vertices, define cₙ = Cₙ^(1/(4n²)) and hₙ = Hₙ^(1/(4n²−4)). These are finite-size exponential-growth estimators, not measurements of a limiting connective constant. Both the change in vertex count and boundary corrections must be accounted for before interpreting their difference.')
table(['n','Qₙ = Hₙ / Cₙ','cₙ: intact','hₙ: punctured'],[[n,f'{H[n]/C[n]:.9f}',f'{math.exp(math.log(C[n])/(4*n*n)):.9f}',f'{math.exp(math.log(H[n])/(4*n*n-4)):.9f}'] for n in range(3,9)],[30,162,156,156])
figure('finite-size.png',504,162,'Figure 3. Exact-count ratios and per-vertex growth estimators. The lines only connect measured values. No extrapolation or fitted asymptotic curve is shown.')
p('The ratios for n=3 through 8 are nonmonotone and show a separation between the even-n and odd-n subsequences. At n=8 the punctured count is about 2.3026% of the intact count for the same outer board. These observations support reporting parity-separated data, but seven nonempty sizes do not identify an asymptotic exponent or distinguish a constant prefactor from a slowly changing correction.')
p('A possible future scaling model separates area, boundary, and logarithmic terms, for example log Cₙ = a(4n²) + b(2n) + c log(2n) + d + lower-order terms. An analogous model for Hₙ would use 4n²−4 visited vertices and could include parity-dependent corrections. This is a model to test, not a theorem asserted here. In particular, this note neither proves that the bulk coefficient a is unchanged by the hole nor estimates a change in it.')

page()
heading('8. Reproducibility, related work, and limits')
heading('Verification and build',2)
p('The package contains a parenthesis frontier counter, a direct-partner frontier counter, a symmetry counter, and a Python checker that branches on complete edge orbits. Full path enumeration checks the 4 × 4 and 6 × 6 punctured boards, including all eight symmetry actions. Edge-orbit constraint search independently checks R₂, R₄, F, and B through side 8. The two full counters agree for intact and punctured boards at every even side from 2 through 16.')
p('From the repository root, run:','small')
p('make all\nmake benchmark\nmake test\nuv sync --group paper\nuv run --group paper python scripts/build_paper.py','small')
p('The first three commands need a C++17 compiler with unsigned __int128 support and Python 3.11 or later. The paper uses pinned dependencies in uv.lock. Each full-board benchmark has a 300-second limit; the symmetry counter stops after 240 seconds or three million active states; each small edge-orbit check has a 60-second limit. All commands run a finite list of cases. Machine-readable counts are decimal strings, so JSON readers cannot silently round them as floating-point values.')
p('results/benchmark.json records timing, peak state count, peak location, and process RSS for both implementations. results/symmetry.json records fixed sets and stabilizer classes. results/verification.json records the separate small-case checks. The committed tables and source checksums support exact-count reproduction; timings and memory use may differ by platform.','small')
heading('Prior work and novelty boundary',2)
p('Connectivity transfer methods and symmetry reduction for Hamiltonian grids are established. Wynn [2] counts symmetry classes for intact square grids and uses quadrant quotients for quarter-turn symmetry. Jacobsen [3] enumerates circuits, walks, and chains by transfer methods. Blanco and Zeilberger [4] give a recent fixed-width generating-function implementation. This note applies those ideas to a precisely specified central puncture and records a complete reproducible table through side 16.')
p('An OEIS search for the consecutive terms 14, 164102, 9684216390 returned no result on 26 September 2026. That is a limited search, not evidence that the sequence has never appeared. The literature check is likewise not exhaustive. This document is a local research draft, not a submitted or accepted paper. The contribution and venue fit still require editorial judgment. No claim of publication priority is made.')
heading('References',2)
p('[1] OEIS Foundation Inc. A003763, Number of (undirected) Hamiltonian cycles on a 2n × 2n square grid of points. https://oeis.org/A003763 (accessed 26 September 2026).','small')
p('[2] Ed Wynn. Enumeration of nonisomorphic Hamiltonian cycles on square grid graphs. arXiv:1402.0545, 2014. https://arxiv.org/abs/1402.0545','small')
p('[3] Jesper Lykke Jacobsen. Exact enumeration of Hamiltonian circuits, walks, and chains in two and three dimensions. Journal of Physics A 40 (2007), 14667-14678. https://arxiv.org/abs/0709.2322','small')
p('[4] Pablo Blanco and Doron Zeilberger. Counting (and Randomly Generating) Hamiltonian Cycles in Rectangular Grids. arXiv:2603.24315, 2026. https://arxiv.org/abs/2603.24315','small')

# Straight ASCII hyphens keep the prose and PDF text consistent.
md_text='\n'.join(md).replace('–','-').replace('—','-')
(ROOT/'paper/paper.md').write_text(md_text)
def footer(canvas,doc):
    canvas.saveState();canvas.setFont('Sans',8);canvas.setFillColor(colors.HexColor('#697182'))
    canvas.drawString(54,31,'Hamiltonian cycles with a central hole | Research-note draft')
    canvas.drawRightString(558,31,str(doc.page));canvas.restoreState()
pdf=OUT/'punctured-grid-cycles.pdf'
doc=SimpleDocTemplate(str(pdf),pagesize=(612,792),leftMargin=54,rightMargin=54,topMargin=44,bottomMargin=48,title='Hamiltonian cycles on square grids with a central 2 x 2 hole',author='Jason Roell')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
reader=PdfReader(pdf)
assert len(reader.pages)==8, f'Expected 8 pages, got {len(reader.pages)}; inspect page overflow'
assert str(H[8]) in ''.join(page.extract_text() for page in reader.pages)
with (ROOT/'results/sequence.csv').open('w',newline='') as f:
    out=csv.writer(f,lineterminator='\n');out.writerow(['n','side','vertices','punctured_cycles','intact_cycles','geometric_orbits'])
    for n in range(1,9):out.writerow([n,2*n,4*n*n-4,H[n],C[n],sym[n]['orbits'] if n>=2 else '0'])
(ROOT/'results/oeis-bfile.txt').write_text(''.join(f'{n} {H[n]}\n' for n in range(1,9)))
files=sorted(p for folder in ('src','scripts') for p in (ROOT/folder).glob('*') if p.is_file())
(ROOT/'results/source-sha256.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in files))
print(f'Built {pdf}; {len(reader.pages)} pages')
