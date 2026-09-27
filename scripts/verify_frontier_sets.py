#!/usr/bin/env python3
"""Compare exact frontier key sets at punctured peak positions, sides 10..16.

Instrument a temporary copy of the production counter, leaving its recurrence
unchanged. Sorted uint64_t arrays are compared byte for byte, not by hash.
Snapshots exclude weights and are removed on completion.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'src/parentheses.cpp'
text = source.read_text()
anchor = '      cur.swap(nxt);\n'
assert text.count(anchor) == 1, 'Counter layout changed; review instrumentation.'
hook = r'''
      if (i + 1 == std::stoi(std::getenv("SNAPSHOT_ROW")) &&
          j + 1 == std::stoi(std::getenv("SNAPSHOT_COL"))) {
        std::vector<uint64_t> keys;
        keys.reserve(cur.size());
        for (const auto &entry : cur) keys.push_back(entry.first);
        std::sort(keys.begin(), keys.end());
        FILE *out = std::fopen(std::getenv("SNAPSHOT_PATH"), "wb");
        if (!out) throw std::runtime_error("Cannot open snapshot");
        size_t written = std::fwrite(keys.data(), sizeof(uint64_t), keys.size(), out);
        int closed = std::fclose(out);
        if (written != keys.size() || closed)
          throw std::runtime_error("Cannot write snapshot");
      }
'''
instrumented = '#include <vector>\n' + text.replace(anchor, anchor + hook)
records = json.loads((ROOT / 'results/benchmark.json').read_text())
results = []
with tempfile.TemporaryDirectory(prefix='frontier-sets-') as directory:
    tmp = Path(directory)
    cpp, binary = tmp / 'counter.cpp', tmp / 'counter'
    cpp.write_text(instrumented)
    subprocess.run(['clang++', '-O3', '-std=c++17', '-I', str(ROOT / 'src'),
                    str(cpp), '-o', str(binary)], check=True, timeout=60)
    for side in (10, 12, 14, 16):
        expected = {int(r['hole']): r for r in records
                    if r['engine'] == 'parentheses' and r['height'] == side}
        row, col = (expected[1][k] for k in ('peak_row', 'peak_col'))
        runs, arrays = [], []
        for hole in (0, 1):
            snapshot = tmp / f'{side}-{hole}.bin'
            env = dict(os.environ, SNAPSHOT_ROW=str(row), SNAPSHOT_COL=str(col),
                       SNAPSHOT_PATH=str(snapshot))
            proc = subprocess.run([str(binary), str(side), str(side), str(hole)],
                                  env=env, capture_output=True, text=True,
                                  check=True, timeout=300)
            actual = json.loads(proc.stdout)
            for key in ('count', 'peak_states', 'peak_row', 'peak_col'):
                assert actual[key] == expected[hole][key], (side, hole, key, actual, expected[hole])
            arrays.append(snapshot.read_bytes())
            assert len(arrays[-1]) == 8 * expected[1]['peak_states'], (side, hole, 'snapshot size')
            runs.append(actual)
            snapshot.unlink()
        assert arrays[0] == arrays[1], (side, row, col, 'frontier key sets differ')
        results.append({'side': side, 'row': row, 'column': col,
                        'states': len(arrays[0]) // 8, 'equal_key_sets': True,
                        'comparison': 'byte-for-byte sorted uint64_t keys; weights excluded',
                        'runs': runs})
        print(f'PASS side {side}: {len(arrays[0]) // 8} identical keys at ({row}, {col})', flush=True)
output = {'source': 'src/parentheses.cpp',
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'scope': 'First punctured peak position at each even side 10..16; no claim for untested layers or sizes.',
          'checks': results}
(ROOT / 'results/frontier-set-verification.json').write_text(json.dumps(output, indent=2) + '\n')
