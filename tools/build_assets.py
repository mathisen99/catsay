#!/usr/bin/env python3
"""Draw and rasterize the original, articulated Moosay mascot. Build-time only."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import math
import subprocess
import argparse
from cat_art import cat

ROOT = Path(__file__).resolve().parents[1]


def cow(phase=0.0, walking=False, blink=False, talking=False, left=False):
    swing = math.sin(phase)
    bob = abs(math.sin(phase)) * 3 if walking else math.sin(phase) * 1.2
    legs = []
    for x, offset, far in [(113, math.pi, True), (234, 0, True), (91, 0, False), (211, math.pi, False)]:
        angle = math.sin(phase + offset) * 22 if walking else 0
        color = '#a9bbb1' if far else 'url(#milk)'
        legs.append(f'''<g transform="rotate({angle} {x} 174)">
        <path d="M{x-13} 165 Q{x-20} 193 {x-13} 223 Q{x} 232 {x+13} 221 L{x+15} 169Z" fill="{color}"/>
        <path d="M{x-14} 214 Q{x} 219 {x+13} 212 L{x+14} 228 Q{x+2} 236 {x-15} 228Z" fill="#304740"/>
        <path d="M{x} 222V230" stroke="#789086" stroke-width="2"/></g>''')
    eyes = ('<path d="M251 107q9 8 18 0 M290 106q8 8 15-1" fill="none" stroke-width="4"/>' if blink else '''
        <ellipse cx="262" cy="107" rx="9" ry="13" fill="#203a32"/>
        <ellipse cx="298" cy="105" rx="8" ry="12" fill="#203a32"/>
        <circle cx="265" cy="103" r="3.2" fill="white" stroke="none"/>
        <circle cx="301" cy="101" r="3" fill="white" stroke="none"/>''')
    mouth = ('<ellipse cx="288" cy="151" rx="9" ry="7" fill="#6f3c42"/><path d="M283 154q5-4 10 0" stroke="#f2a7ac" stroke-width="3"/>' if talking else '<path d="M278 148q10 10 20-1" fill="none" stroke-width="3"/>')
    flip = 'translate(360 0) scale(-1 1)' if left else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="360" height="260" viewBox="0 0 360 260">
    <defs>
      <linearGradient id="milk" x2="0.3" y2="1"><stop stop-color="#fffdf0"/><stop offset=".58" stop-color="#f2f0dc"/><stop offset="1" stop-color="#c9d4c2"/></linearGradient>
      <linearGradient id="nose" x2="0.2" y2="1"><stop stop-color="#ffbfb3"/><stop offset="1" stop-color="#df8b91"/></linearGradient>
      <linearGradient id="spot" x2="0.8" y2="1"><stop stop-color="#41564e"/><stop offset="1" stop-color="#243b34"/></linearGradient>
      <linearGradient id="scarf" x2=".7" y2="1"><stop stop-color="#b8e882"/><stop offset="1" stop-color="#4ea780"/></linearGradient>
      <linearGradient id="horn" x2="0" y2="1"><stop stop-color="#fff0b6"/><stop offset="1" stop-color="#cfaa6f"/></linearGradient>
    </defs>
    <g transform="{flip}" stroke="#263e34" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round">
    <ellipse cx="187" cy="240" rx="119" ry="10" fill="#0b211b" opacity=".24" stroke="none"/>
    <g transform="translate(0 {-bob})">
    <path d="M67 129 C{20+swing*7} 121 {48+swing*14} 76 {22+swing*10} 86" fill="none" stroke-width="7"/>
    <path d="M{23+swing*10} 80q-23-5-14 17q15 4 20-11" fill="url(#spot)"/>
    {''.join(legs[:2])}
    <path d="M134 185q-9 20 15 23h22q22-9 9-26" fill="url(#nose)"/>
    <path d="M145 202v9m20-10v10" stroke="#d5878c" stroke-width="8"/>
    <path d="M63 117 C65 84 111 78 160 84 C202 77 240 90 256 122 L247 166 C231 203 188 201 151 198 C100 204 61 186 60 154Z" fill="url(#milk)"/>
    <path d="M99 87q-19 23-1 39t34 9q20-8 10-28l-7-23" fill="url(#spot)" stroke="none"/>
    <path d="M186 91q-26 18-16 42t37 8q19-11 24-29" fill="url(#spot)" stroke="none"/>
    <path d="M70 152q34-17 43 12t-17 27q-24-8-31-25" fill="url(#spot)" stroke="none"/>
    <path d="M128 178q20 10 40 2" fill="none" stroke="#fffef4" opacity=".8"/>
    {''.join(legs[2:])}
    <path d="M231 144l-25 36 28-3-1 20 24-44" fill="url(#scarf)"/>
    <path d="M218 132q23 28 62 15l-4 18q-40 13-64-13Z" fill="url(#scarf)"/>
    <g transform="rotate({swing*2} 268 130)">
    <path d="M240 68q-21-10-14-31q5 13 22 17" fill="url(#horn)"/>
    <path d="M290 56q14-11 12-26q19 25 3 37" fill="url(#horn)"/>
    <path d="M241 73q-33-24-47-3q8 27 43 19" fill="url(#milk)"/>
    <path d="M229 79q-16-13-25-7q8 10 22 12" fill="#eaa8a1" stroke="none"/>
    <path d="M301 67q24-24 41-8q0 23-32 29" fill="url(#milk)"/>
    <path d="M314 74q12-13 20-12q-2 11-17 15" fill="#eaa8a1" stroke="none"/>
    <path d="M232 86q-1-30 35-32q39-9 47 25l3 42q-1 36-44 39q-47-2-48-34Z" fill="url(#milk)"/>
    <path d="M236 73q20-13 33 3q8 10-3 30t-36 15" fill="url(#spot)" stroke="none"/>
    <path d="M257 58l3-13 12 9 10-12 4 15" fill="#f3efda"/>
    <path d="M285 88q10-6 18 0" fill="none" stroke-width="3"/>
    {eyes}
    <ellipse cx="247" cy="127" rx="10" ry="5" fill="#e8aaa0" opacity=".7" stroke="none"/>
    <path d="M253 124q22-12 54-5q28 4 22 25q-4 24-42 23q-41 1-44-20q-2-13 10-23Z" fill="url(#nose)"/>
    <path d="M256 130q17-9 43-5" fill="none" stroke="#ffd9c9" stroke-width="4"/>
    <ellipse cx="263" cy="139" rx="4" ry="3" fill="#98585f" stroke="none"/>
    <ellipse cx="314" cy="136" rx="4" ry="3" fill="#98585f" stroke="none"/>
    {mouth}
    </g>
    <g transform="rotate({swing*8} 267 169)"><path d="M263 168h8v7h-8Z" fill="#edce7b" stroke-width="2"/>
    <path d="M258 180q0-12 10-12t10 12l4 7q-14 8-28 0Z" fill="url(#horn)" stroke-width="2.5"/>
    <circle cx="268" cy="189" r="3" fill="#8a754d" stroke="none"/>
    <path d="M261 177v6" stroke="#fff2ba" stroke-width="3"/></g>
    </g></g></svg>'''


def build(item):
    name, svg, character = item
    root = ROOT / 'assets' / 'cat' if character == 'cat' else ROOT / 'assets'
    source = root / 'svg' / (name + '.svg')
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('\n'.join(line.rstrip() for line in svg.splitlines()) + '\n')
    for size in (180, 270, 360):
        dest = root / str(size) / (name + '.png')
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['magick', '-background', 'none', str(source), '-resize', str(size), '-strip', 'PNG32:' + str(dest)], check=True, capture_output=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--character', choices=('cat', 'cow', 'all'), default='cat')
    args = parser.parse_args()
    frames = []
    for character in ('cat', 'cow') if args.character == 'all' else (args.character,):
        draw = cat if character == 'cat' else cow
        for left in (False, True):
            direction = 'left' if left else 'right'
            for n in range(12):
                frames.append((f'{direction}-walk-{n:02}', draw(n/12*math.tau, walking=True, left=left), character))
            for n in range(8):
                for mood in ('idle', 'talk', 'blink'):
                    frames.append((f'{direction}-{mood}-{n:02}', draw(n/8*math.tau, blink=mood=='blink', talking=mood=='talk', left=left), character))
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(build, frames))
    print(f'Built {len(frames)} poses in three sizes.')
