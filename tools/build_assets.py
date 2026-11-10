#!/usr/bin/env python3
"""Draw and rasterize the articulated Catsay mascot. Build-time only."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import math
import subprocess
from tempfile import TemporaryDirectory
from cat_art import cat

ROOT = Path(__file__).resolve().parents[1]


def build(item):
    name, svg = item
    root = ROOT / 'assets'
    with TemporaryDirectory(prefix='catsay-art-') as work:
        source = Path(work) / (name + '.svg')
        source.write_text(svg)
        for size in (180, 270, 360):
            dest = root / str(size) / (name + '.png')
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['magick', '-background', 'none', str(source), '-resize', str(size), '-strip', 'PNG32:' + str(dest)], check=True, capture_output=True)


if __name__ == '__main__':
    frames = []
    for left in (False, True):
        direction = 'left' if left else 'right'
        for n in range(12):
            frames.append((f'{direction}-walk-{n:02}', cat(n/12*math.tau, walking=True, left=left)))
        for n in range(8):
            for mood in ('idle', 'talk', 'blink'):
                frames.append((f'{direction}-{mood}-{n:02}', cat(n/8*math.tau, blink=mood=='blink', talking=mood=='talk', left=left)))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(build, frames))
    print(f'Built {len(frames)} poses in three sizes.')
