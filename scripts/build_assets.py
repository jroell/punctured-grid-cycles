#!/usr/bin/env python3
"""Generate manuscript figures, exact tables, and both OEIS b-files."""
import csv
import hashlib
import json
import math
import re
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
FIG=ROOT/'paper/figures';FIG.mkdir(parents=True,exist_ok=True)
rows=json.loads((ROOT/'results/benchmark.json').read_text())
original_rows=list(rows)
base={r['width']//2:r for r in rows if r['engine']=='parentheses' and r['hole']}
intact={r['width']//2:r for r in rows if r['engine']=='parentheses' and not r['hole']}
sym={r['n']:r for r in json.loads((ROOT/'results/symmetry.json').read_text())}
verification=json.loads((ROOT/'results/verification.json').read_text())
assert set(base)==set(range(1,9)) and set(sym)==set(range(2,9))
assert any(r['method']=='edge-orbit search' and r['side']==8 for r in verification)
for n in base:
    matches=[r['count'] for r in rows if r['width']==2*n and r['hole']]
    assert len(matches)==2 and matches[0]==matches[1]
extension_path=ROOT/'results/extension-flat.json'
symmetry_path=ROOT/'results/symmetry-extension.json'
if extension_path.exists() and symmetry_path.exists():
    extended=json.loads(extension_path.read_text())
    fixed={r['n']:r for r in json.loads(symmetry_path.read_text()) if 'orbits' in r}
    for n in (9,10):
        group=[r for r in extended if r['width']==2*n]
        if n not in fixed or len(group)!=4:
            break
        for hole in (False,True):
            pair=[r['count'] for r in group if r['hole']==hole]
            assert len(pair)==2 and pair[0]==pair[1], (n,hole,pair)
        rows.extend(group)
        base[n]=next(r for r in group if r['engine']=='parentheses' and r['hole'])
        intact[n]=next(r for r in group if r['engine']=='parentheses' and not r['hole'])
        sym[n]=fixed[n]
maximum=max(base)
H={n:int(r['count']) for n,r in base.items()}
C={n:int(r['count']) for n,r in intact.items()}
for n in range(2,maximum+1):
    r=sym[n]
    assert H[n]==int(r['raw']), (n,'symmetry/raw mismatch')
    assert 8*int(r['orbits'])==H[n]+int(r['r180'])+2*int(r['r90'])+2*int(r['axis'])+2*int(r['diagonal'])
reference=json.loads((ROOT/'results/oeis-a003763.json').read_text())['counts_by_n']
for n in range(1,maximum+1):
    assert C[n]==int(reference[str(n)]), (n,'OEIS mismatch')
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
ns=list(range(3,maximum+1))
for parity,label,marker in [(0,'n even','o'),(1,'n odd','s')]:
    xs=[n for n in ns if n%2==parity]
    axs[0].plot([2*n for n in xs],[math.log(H[n]/C[n]) for n in xs],marker=marker,label=label)
axs[0].set(xlabel='Side length 2n',ylabel='Log count ratio log(H / C)',xticks=list(range(6,2*maximum+1,2)));axs[0].legend(frameon=False,fontsize=9)
axs[1].plot([2*n for n in ns],[math.exp(math.log(C[n])/(4*n*n)) for n in ns],marker='o',label='Intact',color='#737b8c')
axs[1].plot([2*n for n in ns],[math.exp(math.log(H[n])/(4*n*n-4)) for n in ns],marker='o',label='Punctured',color='#6844a5')
axs[1].set(xlabel='Side length 2n',ylabel='Per-vertex growth estimate',xticks=list(range(6,2*maximum+1,2)));axs[1].legend(frameon=False,fontsize=9)
fig.tight_layout();fig.savefig(FIG/'finite-size.png');fig.savefig(FIG/'finite-size.pdf');plt.close(fig)


TEX=ROOT/'paper/latex/generated';TEX.mkdir(parents=True,exist_ok=True)
def table_file(name,columns,headers,data):
    out=[r'\begin{tabular}{'+columns+'}',r'\toprule', ' & '.join(headers)+r' \\',r'\midrule']
    out.extend(' & '.join(map(str,row))+r' \\' for row in data)
    out.extend([r'\bottomrule',r'\end{tabular}'])
    (TEX/(name+'.tex')).write_text('\n'.join(out)+'\n',encoding='ascii')
table_file('raw','rrr',[r'$n$',r'$|V(G_n)|$',r'$H_n$'],[[n,4*n*n-4,H[n]] for n in range(1,maximum+1)])
table_file('metrics','rrrrr',[r'$2n$', 'Hole peak','Intact peak','Seconds','RSS (MiB)'],[[2*n,f"{base[n]['peak_states']:,}",f"{intact[n]['peak_states']:,}",f"{base[n]['seconds']:.6f}",f"{base[n]['max_rss_mib']:.3f}"] for n in range(2,maximum+1)])
table_file('fixed','rrrrr',[r'$n$',r'$R_2$',r'$R_4$',r'$F$',r'$B$'],[[n,sym[n]['r180'],sym[n]['r90'],sym[n]['axis'],sym[n]['both_axes']] for n in range(2,maximum+1)])
table_file('orbits','rr',[r'$n$',r'$O_n$'],[[n,sym[n]['orbits'] if n>=2 else 0] for n in range(1,maximum+1)])
labels={'trivial':'Identity only','one_axis':'One axial reflection','half_turn_only':r'$180^\circ$ rotation only','both_axes':'Both axial reflections','quarter_turn':'Quarter-turn rotations','all_d4':r'Full $D_4$'}
table_file('classes','lr',['Exact stabilizer','Number of orbits'],[[labels[k],v] for k,v in sym[8]['classes'].items()]+[['Total',sym[8]['orbits']]])
table_file('growth','rrrrr',[r'$n$',r'$H_n/C_n$',r'$\log Q_n$',r'$c_n$',r'$h_n$'],[[n,f'{H[n]/C[n]:.9f}',f'{math.log(H[n]/C[n]):.9f}',f'{math.exp(math.log(C[n])/(4*n*n)):.9f}',f'{math.exp(math.log(H[n])/(4*n*n-4)):.9f}'] for n in range(3,maximum+1)])
(TEX/'values.tex').write_text(
    rf'\newcommand{{\MaximumN}}{{{maximum}}}'+'\n'+
    rf'\newcommand{{\MaximumSide}}{{{2*maximum}}}'+'\n'+
    rf'\newcommand{{\RawSixteen}}{{{H[8]}}}'+'\n'+
    rf'\newcommand{{\OrbitSixteen}}{{{sym[8]["orbits"]}}}'+'\n'+
    rf'\newcommand{{\PeakStates}}{{{base[8]["peak_states"]:,}}}'+'\n'+
    rf'\newcommand{{\RunSeconds}}{{{base[8]["seconds"]:.2f}}}'+'\n'+
    rf'\newcommand{{\PeakMemory}}{{{base[8]["max_rss_mib"]:.1f}}}'+'\n',encoding='ascii')
with (ROOT/'results/sequence.csv').open('w',newline='') as f:
    out=csv.writer(f,lineterminator='\n');out.writerow(['n','side','vertices','punctured_cycles','intact_cycles','geometric_orbits'])
    for n in range(1,maximum+1):out.writerow([n,2*n,4*n*n-4,H[n],C[n],sym[n]['orbits'] if n>=2 else '0'])
(ROOT/'results/oeis-bfile.txt').write_text(''.join(f'{n} {H[n]}\n' for n in range(1,maximum+1)))
(ROOT/'results/oeis-orbits-bfile.txt').write_text(''.join(f'{n} {sym[n]["orbits"] if n>=2 else 0}\n' for n in range(1,maximum+1)))
for name,values in [('raw',H),('orbits',{n:int(sym[n]['orbits']) if n>=2 else 0 for n in H})]:
    path=ROOT/f'paper/submissions/oeis-{name}.md'
    text=path.read_text()
    text=re.sub(r'^Data: .*$', 'Data: '+', '.join(str(values[n]) for n in range(1,maximum+1)), text, flags=re.MULTILINE)
    text=re.sub(r'through n=\d+',f'through n={maximum}',text)
    path.write_text(text)
metadata=ROOT/'paper/submissions/arxiv-metadata.md'
metadata.write_text(re.sub(r'1 <= n <= \d+',f'1 <= n <= {maximum}',metadata.read_text()))
print('Generated figures, six LaTeX tables, both OEIS b-files, and submission data.')
