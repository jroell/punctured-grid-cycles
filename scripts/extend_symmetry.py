#!/usr/bin/env python3
"""Extend fixed-set and orbit tables to n=9,10 using the flat-map backend."""
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/symmetry-extension.json'
rows = json.loads(OUT.read_text()) if OUT.exists() else []
for n in (9, 10):
    row = next((r for r in rows if r['n'] == n), None)
    if row is None:
        row = {'n': n, 'side': 2*n, 'measurements': {}}
        rows.append(row)
    for mode in ('half', 'quarter'):
        if mode not in row['measurements']:
            print(f'Starting n={n} {mode}', flush=True)
            run = subprocess.run([str(ROOT / 'build/symmetry-flat'), str(n), mode],
                                 capture_output=True, text=True, timeout=1860, check=True)
            row['measurements'][mode] = {**json.loads(run.stdout), 'row_profile': run.stderr}
            OUT.write_text(json.dumps(rows, indent=2) + '\n')
            print(run.stdout.strip(), flush=True)
    sources = json.loads((ROOT / 'results/extension-flat.json').read_text())
    raw = [r['count'] for r in sources if r['width'] == 2*n and r['hole']]
    if len(raw) != 2:
        print(f'n={n}: fixed counts saved; waiting for both raw counters', flush=True)
        continue
    assert raw[0] == raw[1], (n, raw)
    h = int(raw[0])
    r2 = int(row['measurements']['half']['rotation'])
    f = int(row['measurements']['half']['reflection'])
    r4 = int(row['measurements']['quarter']['rotation'])
    b = int(row['measurements']['quarter']['reflection'])
    numerator = h + r2 + 2*r4 + 2*f
    assert numerator % 8 == 0
    parts = {'trivial': (h-r2-2*f+2*b, 8), 'one_axis': (f-b, 2),
             'half_turn_only': (r2-r4-b, 4), 'both_axes': (b, 2),
             'quarter_turn': (r4, 2), 'all_d4': (0, 1)}
    classes = {}
    for name, (a, divisor) in parts.items():
        assert a >= 0 and a % divisor == 0, (n, name, a, divisor)
        classes[name] = a // divisor
    assert sum(classes.values()) == numerator // 8
    assert 8*classes['trivial'] + 4*(classes['one_axis']+classes['half_turn_only']) + 2*(classes['both_axes']+classes['quarter_turn']) == h
    assert n % 2 == 0 or r4 == 0
    row.update(raw=str(h), r180=str(r2), r90=str(r4), axis=str(f), both_axes=str(b),
               diagonal='0', orbits=str(numerator//8), classes={k: str(v) for k,v in classes.items()})
    OUT.write_text(json.dumps(rows, indent=2) + '\n')
    print(f'PASS n={n}: {row["orbits"]} orbits', flush=True)
