#!/usr/bin/env python3
"""Record larger full-board counts separately, with bounded serial runs."""
import argparse
import json
import time
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--backend', choices=('std', 'flat'), default='std')
parser.add_argument('--sides', nargs='+', type=int, choices=(18, 20), default=[18, 20])
args = parser.parse_args()
OUT = ROOT / ('results/extension.json' if args.backend == 'std' else 'results/extension-flat.json')


rows = json.loads(OUT.read_text()) if OUT.exists() else []
for side in args.sides:
    for hole in (True, False):
        for engine in ('parentheses', 'partners'):
            if any(r['width'] == side and r['hole'] == hole and r['engine'] == engine for r in rows):
                continue
            print(f'Starting {engine}: side={side}, hole={hole}', flush=True)
            binary = engine + ('-flat' if args.backend == 'flat' else '')
            log = ROOT / f'results/extension-{binary}-{side}-{int(hole)}.txt'
            with log.open('w') as err:
                proc = subprocess.Popen([str(ROOT / 'build' / binary), str(side), str(side), str(int(hole))],
                                        stdout=subprocess.PIPE, stderr=err, text=True)
                start = time.monotonic()
                try:
                    while proc.poll() is None:
                        if time.monotonic() - start > 1800:
                            raise RuntimeError('Run exceeded 1800 seconds')
                        rss = subprocess.run(['ps', '-o', 'rss=', '-p', str(proc.pid)], capture_output=True, text=True)
                        if rss.stdout.strip() and int(rss.stdout) > 48 * 1024**2:
                            raise RuntimeError('Run exceeded 48 GiB RSS')
                        time.sleep(2)
                    stdout, _ = proc.communicate()
                    if proc.returncode:
                        raise RuntimeError(f'{engine} exited {proc.returncode}; see {log}')
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()
            row = json.loads(stdout)
            row['engine'] = engine
            row['backend'] = args.backend
            rows.append(row)
            OUT.write_text(json.dumps(rows, indent=2) + '\n')
            print(json.dumps(row), flush=True)
        pair = [r['count'] for r in rows if r['width'] == side and r['hole'] == hole]
        assert len(pair) == 2 and pair[0] == pair[1], (side, hole, pair)
print('PASS: both representations agree on the extension.', flush=True)
