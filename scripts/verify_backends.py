#!/usr/bin/env python3
"""Compare optional flat-map binaries against every established exact count."""
import json
import subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
checks = []
for expected in json.loads((ROOT / 'results/benchmark.json').read_text()):
    binary = expected['engine'] + '-flat'
    run = subprocess.run([str(ROOT / 'build' / binary), str(expected['height']),
                          str(expected['width']), str(int(expected['hole']))],
                         capture_output=True, text=True, check=True, timeout=300)
    actual = json.loads(run.stdout)
    for key in ('count', 'peak_states', 'peak_row', 'peak_col'):
        assert actual[key] == expected[key], (binary, key, expected, actual)
    checks.append({'binary': binary, **actual})
for expected in json.loads((ROOT / 'results/symmetry.json').read_text()):
    for mode in ('half', 'quarter'):
        run = subprocess.run([str(ROOT / 'build/symmetry-flat'), str(expected['n']), mode],
                             capture_output=True, text=True, check=True, timeout=300)
        actual = json.loads(run.stdout)
        for key in ('rotation', 'reflection', 'peak_states'):
            assert actual[key] == expected['measurements'][mode][key], (mode, key, expected, actual)
        checks.append({'binary': 'symmetry-flat', **actual})
(ROOT / 'results/backend-verification.json').write_text(json.dumps(checks, indent=2) + '\n')
print(f'PASS: {len(checks)} flat-map runs match established counts and peak states.')
