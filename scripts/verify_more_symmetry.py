#!/usr/bin/env python3
"""Try independent quarter-turn and both-axis checks at sides 10 and 12."""
import json
from pathlib import Path
from verify import orbit_count
ROOT = Path(__file__).resolve().parents[1]
expected = {r['side']: r for r in json.loads((ROOT / 'results/symmetry.json').read_text())}
records = []
for side in (10, 12):
    for field, generators in (('r90', [1]), ('both_axes', [4, 5])):
        print(f'Starting independent edge-orbit check: side={side}, field={field}', flush=True)
        row = {'method': 'edge-orbit search', 'side': side, 'field': field, 'time_limit_seconds': 60}
        try:
            actual, nodes, seconds = orbit_count(side, generators, time_limit=60)
            want = int(expected[side][field])
            assert actual == want, f'{side=} {field=}: expected {want} from results/symmetry.json, got {actual}'
            row.update(status='pass', value=actual, nodes=nodes, seconds=seconds)
        except TimeoutError as e:
            row.update(status='timeout', reason=str(e))
        records.append(row)
        (ROOT / 'results/additional-verification.json').write_text(json.dumps(records, indent=2) + '\n')
        print(json.dumps(row), flush=True)
