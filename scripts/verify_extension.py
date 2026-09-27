#!/usr/bin/env python3
"""Validate completed extension records against both encodings and OEIS."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / 'results/extension-flat.json').read_text())
fixed = {r['n']: r for r in json.loads((ROOT / 'results/symmetry-extension.json').read_text())}
reference = json.loads((ROOT / 'results/oeis-a003763.json').read_text())['counts_by_n']
assert len(rows) == 8, f'Expected 8 completed raw runs, got {len(rows)}'
for n in (9, 10):
    for hole in (False, True):
        group = [r for r in rows if r['width'] == 2*n and r['hole'] == hole]
        assert {r['engine'] for r in group} == {'parentheses', 'partners'}, (n, hole, group)
        assert len(group) == 2
        for field in ('count', 'peak_states', 'peak_row', 'peak_col'):
            assert group[0][field] == group[1][field], (n, hole, field, group)
        if not hole:
            assert group[0]['count'] == reference[str(n)], (n, group[0], reference[str(n)])
    h = int(next(r['count'] for r in rows if r['width'] == 2*n and r['hole']))
    s = fixed[n]
    assert int(s['raw']) == h
    r2, r4, f, b = (int(s[k]) for k in ('r180', 'r90', 'axis', 'both_axes'))
    assert 8*int(s['orbits']) == h+r2+2*r4+2*f
    c = {k: int(v) for k, v in s['classes'].items()}
    assert all(v >= 0 for v in c.values())
    assert 2*c['both_axes'] == b
    assert 2*c['quarter_turn'] == r4
    assert 4*c['half_turn_only'] + r4 + b == r2
    assert 2*c['one_axis'] + b == f
    assert 8*c['trivial'] + 4*(c['one_axis']+c['half_turn_only']) + 2*(c['both_axes']+c['quarter_turn']) == h
    assert sum(c.values()) == int(s['orbits'])
    assert n % 2 == 0 or r4 == 0
    print(f'PASS n={n}: raw counts, peak states, OEIS comparison, Burnside, stabilizers, parity')
for r in json.loads((ROOT / 'results/extension.json').read_text()):
    match = next(x for x in rows if x['width'] == r['width'] and x['hole'] == r['hole'] and x['engine'] == r['engine'])
    for field in ('count', 'peak_states', 'peak_row', 'peak_col'):
        assert r[field] == match[field], (field, r, match)
print('PASS: retained standard-map extension runs agree with the flat-map runs')
