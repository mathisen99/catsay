"""Terminal mischief. Graphics-only overlays leave the shell's cells untouched."""

import math
import os
import random
import re
import struct
import subprocess
import time
import zlib

from catsay import ESC, RESET, GREEN, CREAM, Terminal, at, graphics, upload, width


def toy_png(laser=False):
    """A tiny transparent toy, drawn without runtime image dependencies."""
    size = 32
    pixels = bytearray()
    for y in range(size):
        pixels.append(0)  # PNG scanline filter
        for x in range(size):
            radius = math.hypot(x - 15.5, y - 15.5)
            if laser:
                color = (255, 65, 85, max(0, int(240 * (1 - radius / 16) ** 2))) if radius < 16 else (0, 0, 0, 0)
                if radius < 3:
                    color = (255, 230, 220, 255)
            elif radius < 13:
                strand = abs(math.sin((x + y * .55) * .6)) < .25
                color = (245, 211, 151, 255) if strand else (181, 129, 87, 255)
            else:
                color = (0, 0, 0, 0)
            pixels.extend(color)

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))

    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(bytes(pixels))) + chunk(b'IEND', b''))


def capture_screen():
    if not os.environ.get('KITTY_WINDOW_ID'):
        raise RuntimeError('--steal needs a Kitty window; try --yarn or --zoomies instead.')
    try:
        result = subprocess.run(
            ['kitten', '@', '--password', 'catsay-screen', 'get-text', '--self', '--ansi', '--extent', 'screen'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=4, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError('Could not read the Kitty screen. Try --yarn, or see README: Screen stealing.') from error
    if result.returncode:
        raise RuntimeError('--steal needs Kitty screen access. See README: Screen stealing; --yarn needs no setup.')
    # Accept SGR styling only. In particular, never replay OSC, DCS or cursor controls.
    return [safe_line(line) for line in result.stdout.decode('utf-8', 'replace').splitlines()]


def safe_line(line):
    # Remove complete control sequences before extracting printable text and SGR.
    line = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)', '', line)
    line = re.sub(r'\x1b[P_^X].*?\x1b\\', '', line)
    line = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]',
                  lambda match: match[0] if re.fullmatch(r'\x1b\[[0-9;:]*m', match[0]) else '', line)
    return ''.join(re.findall(r'\x1b\[[0-9;:]*m|[^\x00-\x1f\x7f-\x9f]', line))


def screen_words(lines, cols, rows):
    """Locate printable ASCII words, counting wide glyphs before each word."""
    words = []
    for row, line in enumerate(lines[:rows - 1], 1):
        plain = re.sub(r'\x1b\[[0-9;:]*m', '', line)
        for match in re.finditer(r'[A-Za-z_][A-Za-z_0-9.-]{2,13}', plain):
            col = width(plain[:match.start()]) + 1
            if col + len(match[0]) <= cols:
                words.append((row, col, match[0]))
    return words


def repaint(lines, rows, cols, selected=None, removed=0):
    out = f'{ESC}[?7l'
    for row, line in enumerate(lines[:rows], 1):
        out += at(row, 1) + RESET + f'{ESC}[2K' + line
    if selected and removed:
        row, col, word = selected
        out += at(row, col) + RESET + ' ' * min(removed, len(word))
    return out


def play(args):
    stealing = args.steal
    background = capture_screen() if stealing else []
    mode = 'steal' if stealing else 'yarn' if args.yarn else 'laser' if args.laser else 'zoomies' if args.zoomies else 'overlay'
    limit = args.duration or (float('inf') if args.loop else 16 if stealing else 20)
    with Terminal(overlay=not stealing) as term:
        if not term.probe():
            raise RuntimeError('This terminal did not answer the Kitty graphics query. Run directly in Kitty (outside tmux).')
        elapsed = 0.0
        previous = time.monotonic()
        layout = None
        x = -180.0
        paused = False
        direction = 'right'
        laser_x = laser_y = 0.0
        selected = None
        while True:
            started = time.monotonic()
            dt = min(.1, started - previous)
            previous = started
            dimensions = term.size()
            rows, cols, cw, ch = dimensions
            if rows < 10 or cols < 24:
                # Never erase the underlying shell to display a size warning.
                keys = term.keys(.1)
                if b'q' in keys or b'\x1b' in keys:
                    break
                continue
            screen_w, screen_h = cols * cw, rows * ch
            if dimensions != layout:
                sw = min((180, 270, 360), key=lambda size: abs(size - min(args.size, screen_w * .4, screen_h * .65)))
                sh = round(sw * 260 / 360)
                term.load(sw)
                toy_id = random.randint(2100000000, 2200000000)
                term.ids.append(toy_id)
                term.write(upload(toy_png(mode == 'laser'), toy_id))
                layout = dimensions
                laser_x, laser_y = screen_w * .72, screen_h * .7
                candidates = screen_words(background, cols, rows)
                # Prefer words near the lower part of the screen, where a cat can stand.
                candidates = [w for w in candidates if w[0] * ch > sh * .6] or candidates
                selected = random.choice(candidates) if candidates else None
                if stealing and not selected:
                    raise RuntimeError('Nothing to steal yet. Print a few words in your terminal first!')
                previous = time.monotonic()
            if not paused:
                elapsed += dt
            if elapsed >= limit:
                break
            remaining = limit - elapsed
            floor = max(0, screen_h - sh - ch)
            y = floor
            toy = None
            cycle = elapsed % 16
            if mode == 'steal':
                row, col, word = selected
                # The mouth meets the word; later it carries the whole word away.
                destination = max(0, min(screen_w - sw, (col - 1) * cw - sw * .77))
                target = screen_w + sw if cycle > 10 else destination
                y = max(0, min(floor, (row - 1) * ch - sh * .54))
            elif mode == 'yarn':
                ball_x = (screen_w - 36) * (.5 + .43 * math.sin(elapsed * 1.25))
                ball_y = screen_h - ch - 30 - abs(math.sin(elapsed * 3.2)) * ch * 2.4
                target = ball_x - sw * (.78 if ball_x > x + sw / 2 else .22)
                toy = (ball_x, ball_y)
                y -= abs(math.sin(elapsed * 3.2)) * ch * .35
            elif mode == 'laser':
                if int(elapsed / 2.5) != int((elapsed - dt) / 2.5) and not paused:
                    laser_x, laser_y = random.uniform(.12, .88) * screen_w, random.uniform(.35, .9) * screen_h
                target = laser_x - sw * .5
                y = max(0, min(floor, laser_y - sh * .5))
                toy = (laser_x, laser_y)
            else:
                frequency = 2.7 if mode == 'zoomies' else .42
                target = (screen_w - sw) * (.5 + .5 * math.sin(elapsed * frequency))
                if mode == 'zoomies':
                    y -= abs(math.sin(elapsed * 5)) * min(floor, sh * .5)
            if mode != 'steal' and remaining < 2:
                target = screen_w + sw
            speed = args.speed * (5 if mode == 'zoomies' else 2.5 if mode in ('yarn', 'laser') else 1)
            if mode == 'steal':
                speed = max(speed, (screen_w + sw) / 3)
            delta = target - x
            if not paused:
                x += max(-speed * dt, min(speed * dt, delta))
            if abs(delta) > 2:
                direction = 'right' if delta > 0 else 'left'
            if mode == 'steal' and cycle < 10:
                direction = 'right'
            walking = abs(delta) > 5
            pose = f'walk-{int(elapsed * (24 if mode == "zoomies" else 16)) % 12:02}' if walking else f'idle-{int(elapsed * 4) % 8:02}'
            data = (f'{ESC}[?2026h').encode()
            if stealing:
                removed = min(len(word), max(0, int((cycle - 4) * 5)))
                data += repaint(background, rows, cols, selected, removed).encode()
                # Letters hop out of their original cells into the cat's mouth.
                for i in range(removed):
                    age = cycle - 4 - i / 5
                    phase = min(1, max(0, age / .7))
                    origin_x = (col - 1 + i) * cw
                    mouth_x = x + sw * .88 + i * cw
                    px = origin_x + (mouth_x - origin_x) * phase
                    py = (row - 1) * ch + (y + sh * .54 - (row - 1) * ch) * phase - math.sin(phase * math.pi) * ch * 3
                    if 0 <= px < screen_w - cw and 0 <= py < screen_h - ch:
                        data += (at(int(py / ch) + 1, int(px / cw) + 1) + CREAM + word[i] + RESET).encode()
                if cycle > 10:
                    data += (at(max(1, row - 2), max(1, min(cols - 22, col))) + GREEN + 'mine now. thank you.' + RESET).encode()
                if cycle < dt and elapsed > 1:
                    selected = random.choice(screen_words(background, cols, rows))
                    x = -float(sw)
            data += term.sprite(f'{direction}-{pose}', x, y, sw, sh, cw, ch, screen_w)
            if toy:
                tx, ty = (max(0, int(v)) for v in toy)
                data += graphics(a='d', d='i', i=toy_id, p=2, q=2)
                data += at(ty // ch + 1, tx // cw + 1).encode()
                data += graphics(a='p', i=toy_id, p=2, q=2, C=1, X=tx % cw, Y=ty % ch)
            term.write(data + f'{ESC}[?2026l'.encode())
            keys = term.keys(1 / args.fps - (time.monotonic() - started))
            if b'q' in keys or keys == b'\x1b':
                break
            if b'p' in keys:
                paused = not paused
            if b' ' in keys:
                laser_x, laser_y = random.uniform(.12, .88) * screen_w, random.uniform(.35, .9) * screen_h
        return 0
