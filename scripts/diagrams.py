#!/usr/bin/env python3
"""Pinned local D2 rendering, validation, and byte comparison."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NAMES = ('infrastructure-overview', 'network-topology', 'management-architecture',
         'monitoring-alerting', 'services-workloads', 'future-architecture', 'backup-dataflow')
DARK = NAMES[:2]

def call(args):
    subprocess.run(args, check=True, cwd=ROOT)

def validate_svg(path):
    data = path.read_bytes()
    doc = ET.fromstring(data)
    assert doc.tag == '{http://www.w3.org/2000/svg}svg', path
    box = [float(v) for v in doc.attrib['viewBox'].split()]
    assert 100 < box[2] < 7000 and 100 < box[3] < 5000, (path, box)
    labels = [''.join(e.itertext()) for e in doc.iter() if e.tag.endswith('}text')]
    assert labels and all(label.strip() for label in labels), path
    assert len(data) < 2_000_000, path
    print(f'{path.name}: {int(box[2])} × {int(box[3])}, {len(labels)} text labels, XML valid')

def svg_fallback(path):
    # librsvg does not use embedded webfonts. A sans fallback keeps the PNG
    # readable; browsers still use the bundled D2 font first.
    data = path.read_text()
    data = re.sub(r'(font-family:\s*"[^";]+")(?=;)', r'\1, sans-serif', data)
    path.write_text(data)

def render(d2, out):
    for name in NAMES:
        src = ROOT / 'diagrams/src' / (name + '.d2')
        call([d2, '--layout=elk', '--theme=0', '--pad=48', '--omit-version',
              '--salt=' + name, str(src), str(out / (name + '.svg'))])
        svg_fallback(out / (name + '.svg'))
        validate_svg(out / (name + '.svg'))
        if name in DARK:
            # Same geometry and labels; only the palette changes.
            colors = {'#f1f5f9':'#1e293b', '#475569':'#94a3b8', '#0f172a':'#f1f5f9',
                      '#d1fae5':'#064e3b', '#047857':'#34d399', '#ede9fe':'#3b2862',
                      '#7c3aed':'#c4b5fd', '#ccfbf1':'#134e4a', '#0f766e':'#5eead4',
                      '#fef3c7':'#533b12', '#b45309':'#fbbf24', '#1d4ed8':'#93c5fd'}
            source = src.read_text().replace('theme-id: 0', 'theme-id: 200')
            source = re.sub(r'#[0-9a-f]{6}', lambda m: colors.get(m[0], m[0]), source)
            dark_src = out / (name + '-dark.d2')
            dark_src.write_text(source)
            call([d2, '--layout=elk', '--theme=200', '--pad=48', '--omit-version',
                  '--salt=' + name + '-dark', str(dark_src), str(out / (name + '-dark.svg'))])
            dark_src.unlink()
            svg_fallback(out / (name + '-dark.svg'))
            validate_svg(out / (name + '-dark.svg'))
    call(['rsvg-convert', '--width=1600', '--keep-aspect-ratio',
          '--output=' + str(out / 'infrastructure-overview.png'),
          str(out / 'infrastructure-overview.svg')])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['render', 'check', 'lint'])
    args = parser.parse_args()
    d2 = os.environ.get('D2', 'd2')
    version = subprocess.check_output([d2, '--version'], text=True).strip()
    if version not in ('v0.9.0', 'd2 v0.9.0'):
        raise SystemExit('D2 v0.9.0 required for reproducible assets; got ' + version)
    if args.mode == 'lint':
        for name in NAMES:
            call([d2, 'validate', str(ROOT / 'diagrams/src' / (name + '.d2'))])
        print('Seven D2 sources validated.')
        return
    with tempfile.TemporaryDirectory(prefix='public-diagrams-') as temp:
        out = Path(temp)
        render(d2, out)
        target = ROOT / 'diagrams/rendered'
        target.mkdir(exist_ok=True)
        generated = {p.name for p in out.iterdir()}
        if args.mode == 'check':
            existing = {p.name for p in target.iterdir()}
            if generated != existing:
                raise SystemExit('Rendered file inventory differs')
            mismatches = [p.name for p in out.iterdir()
                          if p.read_bytes() != (target / p.name).read_bytes()]
            if mismatches:
                raise SystemExit('Non-reproducible or stale assets: ' + ', '.join(mismatches))
            print('All nine SVGs and the PNG byte-match fresh temporary renders.')
        else:
            for p in out.iterdir():
                (target / p.name).write_bytes(p.read_bytes())

if __name__ == '__main__':
    main()
