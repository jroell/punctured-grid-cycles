#!/usr/bin/env python3
"""Count fixed edge sets and apply Burnside; retain every measured run."""
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
raw=[json.loads(line) for line in (ROOT/'results/benchmark.jsonl').read_text().splitlines()]
counts={r['width']//2:int(r['count']) for r in raw if r['engine']=='parentheses' and r['hole']}
rows=[]
for n in range(2,9):
    values={}
    for mode in ('half','quarter'):
        p=subprocess.run([str(ROOT/'build/symmetry'),str(n),mode],capture_output=True,text=True,check=True,timeout=260)
        values[mode]=json.loads(p.stdout)
        values[mode]['row_profile'] = p.stderr
        print(p.stdout.strip(),flush=True)
    c=counts[n]; r2=int(values['half']['rotation']); f=int(values['half']['reflection'])
    r4=int(values['quarter']['rotation']); b=int(values['quarter']['reflection']); diagonal=int(n==2)
    numerator=c+r2+2*r4+2*f+2*diagonal
    assert numerator%8==0,(n,'Burnside integrality')
    orbits=numerator//8
    if n==2:
        classes={'trivial':0,'one_axis':0,'half_turn_only':0,'both_axes':0,'quarter_turn':0,'all_d4':1}
    else:
        numerators={'trivial':(c-r2-2*f+2*b,8),'one_axis':(f-b,2),
                    'half_turn_only':(r2-r4-b,4),'both_axes':(b,2),'quarter_turn':(r4,2),'all_d4':(0,1)}
        classes={}
        for k,(a,d) in numerators.items():
            assert a>=0 and a%d==0,(n,k,a,d)
            classes[k]=a//d
    assert sum(classes.values())==orbits
    assert 8*classes['trivial']+4*(classes['one_axis']+classes['half_turn_only'])+2*(classes['both_axes']+classes['quarter_turn'])+classes['all_d4']==c
    if n%2:assert r4==0
    row={'n':n,'side':2*n,'raw':str(c),'r180':str(r2),'r90':str(r4),'axis':str(f),'diagonal':str(diagonal),'both_axes':str(b),'orbits':str(orbits),'classes':{k:str(v) for k,v in classes.items()},'measurements':values}
    rows.append(row)
    (ROOT/'results/symmetry.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(f'PASS n={n}: {orbits} geometric orbits',flush=True)
