#!/usr/bin/env python3
"""Run both counters serially, recording exact results and one timing per case."""
import json
import platform
import subprocess
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
RESULTS.mkdir(exist_ok=True)
metadata = {'platform': platform.platform(), 'machine': platform.machine(),
            'compiler': subprocess.check_output(['clang++', '--version'], text=True).strip(),
            'flags': '-O3 -std=c++17 -Wall -Wextra',
            'timing_method': 'One run per case, serial execution; not a repeated benchmark.'}
if platform.system() == 'Darwin':
    for key in ('machdep.cpu.brand_string', 'hw.memsize'):
        metadata[key] = subprocess.check_output(['sysctl', '-n', key], text=True).strip()
(RESULTS / 'environment.json').write_text(json.dumps(metadata, indent=2) + '\n')
known = {2*int(n): int(value) for n, value in json.loads(
    (RESULTS / 'oeis-a003763.json').read_text())['counts_by_n'].items()}
rows = []
profiles = {}
with (RESULTS / 'benchmark.jsonl').open('w') as output:
    for side in range(2, 17, 2):
        for hole in (False, True):
            answers = []
            for engine in ('parentheses', 'partners'):
                start = perf_counter()
                result = subprocess.run([str(ROOT / 'build' / engine), str(side), str(side), str(int(hole))],
                                        capture_output=True, text=True, check=True, timeout=300)
                row = json.loads(result.stdout)
                row['engine'] = engine
                row['wall_seconds'] = perf_counter() - start
                answers.append(row['count'])
                rows.append(row)
                output.write(json.dumps(row) + '\n')
                output.flush()
                profiles[f'{engine}-{side}-{int(hole)}'] = result.stderr
                (RESULTS / 'frontier-profiles.json').write_text(json.dumps(profiles, indent=2) + '\n')
                print(f'{engine} {side} hole={hole}: {row["count"]}; peak={row["peak_states"]}; {row["seconds"]:.3f}s', flush=True)
            assert answers[0] == answers[1], (side, hole, answers)
            if not hole and side in known:
                assert int(answers[0]) == known[side], (side, answers[0], known[side])
(RESULTS / 'benchmark.json').write_text(json.dumps(rows, indent=2) + '\n')
print('PASS: both implementations agree for every case.', flush=True)
