#!/usr/bin/env python3
"""Build the canonical LaTeX manuscript and a portable source archive."""
import hashlib
import re
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / 'paper/latex'
OUT = ROOT / 'output/pdf'
BUILD = ROOT / 'tmp/latex'
NAME = 'roell-punctured-grids'
start = time.monotonic()
for tool in ('tectonic', 'pandoc'):
    if not shutil.which(tool):
        raise SystemExit(f'Missing {tool}; install it and rerun this script.')
subprocess.run([sys.executable, str(ROOT / 'scripts/build_assets.py')], check=True)
BUILD.mkdir(parents=True, exist_ok=True)
subprocess.run(['tectonic', '--keep-logs', '--outdir', str(BUILD), str(TEX / f'{NAME}.tex')], check=True)
log = (BUILD / f'{NAME}.log').read_text()
for problem in ('Overfull', 'undefined references', 'Citation `', 'Reference `'):
    if problem in log:
        raise SystemExit(f'Unresolved LaTeX warning: {problem}; inspect {BUILD}')
OUT.mkdir(parents=True, exist_ok=True)
shutil.copyfile(BUILD / f'{NAME}.pdf', OUT / 'punctured-grid-cycles.pdf')
page_count = len(PdfReader(OUT / 'punctured-grid-cycles.pdf').pages)
metadata = ROOT / 'paper/submissions/arxiv-metadata.md'
text = re.sub(r'^Comments: .*\n\n', '', metadata.read_text(), flags=re.MULTILINE)
text = text.replace('Repository:', f'Comments: {page_count} pages, 3 figures; exact tables and reproducible code.\n\nRepository:')
metadata.write_text(text)

subprocess.run(['pandoc', f'{NAME}.tex', '--from=latex', '--to=gfm',
                '--output', str(ROOT / 'paper/paper.md')], cwd=TEX, check=True)
md = ROOT / 'paper/paper.md'
body = md.read_text()
body = re.sub(r'<embed src="([a-z-]+)\.pdf" />',
              r'<img src="figures/\1.png" alt="Manuscript figure" />', body)
body = re.sub(r'\{#(tab:[a-z]+)\}', r'<a id="\1"></a>', body)
md.write_text('# Hamiltonian cycles on square grids with a central 2 x 2 hole\n\n'
              'Jason Roell\n\n'
              '[PDF](../output/pdf/punctured-grid-cycles.pdf) | '
              '[Canonical LaTeX source](latex/roell-punctured-grids.tex)\n\n' + body)
archive = ROOT / 'output/arxiv-source.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(TEX.rglob('*.tex')):
        z.write(p, p.relative_to(TEX))
    for p in sorted((ROOT / 'paper/figures').glob('*.pdf')):
        z.write(p, 'figures/' + p.name)
files = sorted([*ROOT.glob('src/*'), *ROOT.glob('scripts/*.py')])
(ROOT / 'results/source-sha256.txt').write_text(''.join(
    f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}\n' for p in files if p.is_file()))
print(f'Built PDF and {archive.name} in {time.monotonic() - start:.2f} seconds.')
