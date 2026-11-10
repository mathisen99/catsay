#!/usr/bin/env python3
"""A little familiar for Kitty: an animated cat in a crooked black hat."""
from __future__ import annotations

import argparse
import base64
import fcntl
import math
import os
from pathlib import Path
import random
import select
import signal
import struct
import sys
import termios
import time
import tty
import unicodedata

ASSETS = Path(__file__).resolve().parent / 'assets'
ESC = '\x1b'
RESET = ESC + '[0m'
GREEN = ESC + '[38;2;170;211;144m'
MUTED = ESC + '[38;2;104;143;124m'
CREAM = ESC + '[38;2;245;239;213m'
COW_SAYINGS = [
    'Moo.\nI live in your terminal now.',
    'Outstanding in my field.\nStill no idea what a Kubernetes is.',
    'You write the code.\nI will handle the grass.',
    'Have you tried turning it\noff and moo again?',
    'Tiny reminder:\nunclench your jaw. Have some water.',
    'No thoughts.\nJust excellent pasture management.',
    'Your build passed.\nI did not check. I believe in you.',
]
SAYINGS = [
    'Hello, Linux.chat!\nI have claimed this terminal.',
    'If you are watching this on Discord:\nhello. This is apparently\nwhat we do with computers now.',
    'You are probably wondering\nwhy there is a cat in your shell.',
    'A user got bored and told an LLM:\n"Upgrade cowsay to 2026."',
    'That was the entire specification.\nNobody mentioned a cat.\nI attended the meeting anyway.',
    'The original program printed a cow.\nIt was finished. It worked.\nNaturally, this could not stand.',
    'Now your GPU renders my whiskers\nso I can tell you absolutely nothing\nin considerably higher fidelity.',
    'The cow did not survive the rebrand.\nIt is still available under\n"--character cow". Very undignified.',
    'First I was just a speech bubble.\nThe LLM had deleted my entire body.\nAll nine tests passed. Incredible.',
    'They fixed it. I got a hat.\nThis is apparently\nthe software development lifecycle.',
    'You could have finished a task.\nInstead, you commissioned\na tiny unemployed wizard.',
    'My job is to walk six inches,\nmake a remark, and stop.\nI am considering a management role.',
    'No subscription. No cloud.\nJust a local idiot in a hat.\nFinally, software you can trust.',
    'You own the computer.\nI own the terminal.\nThe cursor is shared custody.',
    'Please stop calling this\n"scope creep".\nI prefer "cat acquisition".',
    'You can press q to evict me.\nBut look at this hat.\nThink about what you are doing.',
    'Anyway. Back to work, Linux.chat.\nI will see myself out.\nThe hat is coming with me.',
    'The terminal is yours again.\nPlease try not to invent\nanother animal while I am gone.',
]


def graphics(payload=b'', **keys):
    return (f'{ESC}_G' + ','.join(f'{k}={v}' for k, v in keys.items()) + ';').encode() + payload + b'\x1b\\'


def upload(data, image_id):
    encoded = base64.b64encode(data)
    chunks = []
    for start in range(0, len(encoded), 4096):
        piece = encoded[start:start+4096]
        keys = dict(a='t', f=100, i=image_id, q=2) if start == 0 else {}
        chunks.append(graphics(piece, **keys, m=int(start+4096 < len(encoded))))
    return b''.join(chunks)


def at(row, col):
    return f'{ESC}[{max(1, row)};{max(1, col)}H'


def clean(text):
    return ''.join(c for c in text.expandtabs(4) if c == '\n' or not unicodedata.category(c).startswith('C'))


def width(text):
    return sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1 for c in text)


def wrap(text, columns):
    lines = []
    for paragraph in clean(text).split('\n'):
        line = ''
        for word in paragraph.split():
            if line and width(line + ' ' + word) > columns:
                lines.append(line)
                line = ''
            if line:
                line += ' '
            for char in word:
                if width(line + char) > columns:
                    lines.append(line)
                    line = ''
                line += char
        lines.append(line)
    return lines


def pages(messages, columns, height=4):
    result = []
    for message in messages:
        lines = wrap(message, columns)
        result.extend('\n'.join(lines[n:n+height]) for n in range(0, len(lines), height))
    return result


class Terminal:
    def __init__(self):
        self.input = None
        self.saved = None
        self.ids = []
        self.previous = None
        self.handlers = {}

    def write(self, data):
        sys.stdout.buffer.write(data.encode() if isinstance(data, str) else data)
        sys.stdout.buffer.flush()

    def __enter__(self):
        self.input = open('/dev/tty', 'rb', buffering=0)
        self.saved = termios.tcgetattr(self.input)
        tty.setcbreak(self.input)
        try:
            for sig in (signal.SIGTERM, signal.SIGHUP):
                self.handlers[sig] = signal.signal(sig, self.stop)
            self.write(f'{ESC}[?1049h{ESC}[?25l{ESC}[2J')
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    @staticmethod
    def stop(signum, frame):
        raise KeyboardInterrupt

    def __exit__(self, *args):
        try:
            self.write(self.delete_assets() + f'{ESC}[?2026l{RESET}{ESC}[?25h{ESC}[?1049l'.encode())
        finally:
            if self.saved is not None:
                termios.tcsetattr(self.input, termios.TCSADRAIN, self.saved)
            if self.input:
                self.input.close()
            for sig, handler in self.handlers.items():
                signal.signal(sig, handler)

    def size(self):
        rows, cols, px, py = struct.unpack('HHHH', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, b'\0'*8))
        rows, cols = rows or 24, cols or 80
        return rows, cols, (px // cols if px else 10), (py // rows if py else 20)

    def keys(self, timeout):
        ready, _, _ = select.select([self.input], [], [], max(0, timeout))
        return os.read(self.input.fileno(), 4096) if ready else b''

    def probe(self):
        self.write(graphics(b'AAAA', a='q', i=918273, s=1, v=1, f=24, t='d'))
        response = b''
        deadline = time.monotonic() + 1.0
        while time.monotonic() < deadline:
            response += self.keys(deadline - time.monotonic())
            if b'i=918273;OK' in response:
                return True
        return False

    def delete_assets(self):
        data = b''.join(graphics(a='d', d='I', i=i, q=2) for i in self.ids)
        self.ids = []
        self.previous = None
        return data

    def load(self, size, character='cat'):
        self.write(self.delete_assets())
        self.frames = {}
        first = random.randint(1000000, 2000000000)
        root = ASSETS / 'cat' if character == 'cat' else ASSETS
        for index, path in enumerate(sorted((root / str(size)).glob('*.png'))):
            image_id = first + index
            self.ids.append(image_id)
            self.frames[path.stem] = image_id
            self.write(upload(path.read_bytes(), image_id))
        if not self.frames:
            raise RuntimeError('Missing bundled sprites. Run python tools/build_assets.py to rebuild them.')

    def sprite(self, name, x, y, sw, sh, cw, ch, screen_width):
        image_id = self.frames[name]
        result = b''
        if self.previous is not None:
            result += graphics(a='d', d='i', i=self.previous, p=1, q=2)
        crop = max(0, -int(x))
        visible = min(sw-crop, screen_width-max(0, int(x)))
        if visible > 0:
            x = max(0, int(x))
            result += at(int(y)//ch+1, x//cw+1).encode()
            result += graphics(a='p', i=image_id, p=1, q=2, C=1, X=x % cw, Y=int(y) % ch, x=crop, w=visible, h=sh)
            self.previous = image_id
        else:
            self.previous = None
        return result


def bubble(message, revealed, cols, top, center):
    full_lines = message.split('\n')
    inner = min(cols-8, max(18, *(width(line) for line in full_lines)))
    left = max(2, min(cols-inner-5, int(center-inner/2)-2))
    visible = message[:revealed].split('\n')
    result = at(top, left) + GREEN + '╭' + '─'*(inner+2) + '╮'
    for index in range(len(full_lines)):
        line = visible[index] if index < len(visible) else ''
        result += at(top+index+1, left) + GREEN + '│ ' + CREAM + line + ' '*(inner-width(line)) + GREEN + ' │'
    result += at(top+len(full_lines)+1, left) + GREEN + '╰' + '─'*(inner+2) + '╯'
    tail = max(left+3, min(left+inner, int(center)))
    result += at(top+len(full_lines)+2, tail) + GREEN + '╲' + RESET
    return result


def run(args, messages):
    with Terminal() as term:
        if not term.probe():
            raise RuntimeError('This terminal did not answer the Kitty graphics query. Run directly in Kitty (outside tmux).')
        layout = None
        state = 'enter'
        x = 0.0
        direction = 'right'
        elapsed = talk_time = 0.0
        index = 0
        paused = False
        previous_time = time.monotonic()
        while True:
            frame_start = time.monotonic()
            dt = min(.1, frame_start-previous_time)
            previous_time = frame_start
            dimensions = term.size()
            if dimensions != layout:
                rows, cols, cw, ch = dimensions
                if cols < 36 or rows < 16:
                    term.write(f'{ESC}[2J{ESC}[H{CREAM}Give this {args.character} at least 36 columns × 16 rows.{RESET}')
                    # Erasing the screen also discards Kitty's cached images.
                    layout, state = None, 'enter'
                    if b'q' in term.keys(.1):
                        break
                    continue
                screen_width = cols*cw
                available_height = max(130, (rows-10)*ch)
                candidates = [s for s in (180, 270, 360) if s <= screen_width*.7 and round(s*260/360) <= available_height]
                sw = min(candidates, key=lambda s: abs(s-args.size)) if candidates else 180
                sh = round(sw*260/360)
                # Kitty's ED2 command frees image data, including images without
                # placements. Clear BEFORE uploading the poses, never afterward.
                term.write(f'{ESC}[2J')
                term.load(sw, args.character)
                page_height = 2 if rows < 22 else 4
                y = max(7*ch, (rows-3)*ch-sh)
                speech_top = max(3, int(y/ch)-page_height-2)
                dialogue = pages(messages, min(46, cols-10), page_height)
                index = min(index, len(dialogue)-1)
                if layout is None:
                    x = -float(sw)
                else:
                    x = max(-sw, min(x, screen_width-sw))
                target = (screen_width-sw)*.48
                layout = dimensions
                previous_time = time.monotonic()
            if not paused:
                elapsed += dt
                if args.duration and elapsed >= args.duration:
                    break
                if state in ('enter', 'wander', 'exit'):
                    destination = screen_width+sw*.1 if state == 'exit' else target
                    step = args.speed*dt
                    delta = destination-x
                    direction = 'right' if delta >= 0 else 'left'
                    x += max(-step, min(step, delta))
                    if abs(destination-x) < 1:
                        if state == 'exit':
                            break
                        state, talk_time = 'talk', 0.0
                else:
                    talk_time += dt
                    message = dialogue[index]
                    if talk_time > len(message)/args.typing_speed + args.hold:
                        index += 1
                        if index >= len(dialogue):
                            if args.loop:
                                index = 0
                            else:
                                state = 'exit'
                        if state != 'exit':
                            if args.pet:
                                state = 'wander'
                                target = random.uniform(.08, .85)*(screen_width-sw)
                            else:
                                talk_time = 0.0

            walking = state in ('enter', 'wander', 'exit')
            if walking:
                pose = f'walk-{int(elapsed*16)%12:02}'
            else:
                typing = talk_time < len(dialogue[index])/args.typing_speed
                blink = elapsed % 4.3 > 4.13
                mood = 'blink' if blink else 'talk' if typing and int(elapsed*9)%2 else 'idle'
                pose = f'{mood}-{int(elapsed*4)%8:02}'
            # Synchronized output makes sprite replacement and text a single visible frame.
            out = f'{ESC}[?2026h'
            # Erase only speech rows; sprites use their own graphics placements.
            for row in range(speech_top, min(rows-2, speech_top+page_height+3)):
                out += at(row, 1) + f'{ESC}[2K'
            subtitle = '   /   a little company for your terminal' if cols >= 58 else ''
            title = 'c a t s a y' if args.character == 'cat' else 'm o o s a y'
            out += at(2, 4) + GREEN + title + MUTED + subtitle
            out += at(rows-2, 4) + MUTED + ('─'*(cols-7))
            footer = 'space  next thought     p  pause     q  leave'
            if cols < 50:
                footer = 'space next · p pause · q leave'
            if paused:
                footer = 'paused                  p  resume    q  leave'
            out += at(rows-1, max(2, (cols-len(footer))//2)) + MUTED + footer[:cols-3] + RESET
            if state == 'talk':
                head = (x+sw*(.77 if direction == 'right' else .23))/cw
                out += bubble(dialogue[index], int(talk_time*args.typing_speed), cols, speech_top, head)
            data = out.encode() + term.sprite(f'{direction}-{pose}', x, y, sw, sh, cw, ch, screen_width)
            term.write(data + f'{ESC}[?2026l'.encode())
            keys = term.keys(1/args.fps-(time.monotonic()-frame_start))
            if b'q' in keys or b'\x1b' == keys:
                break
            if b'p' in keys:
                paused = not paused
            if b' ' in keys and state == 'talk':
                talk_time = len(dialogue[index])/args.typing_speed + args.hold
        return 0


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('must be a finite number greater than zero')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('message', nargs='*', help='what your companion should say; also accepts piped text')
    parser.add_argument('--character', choices=('cat', 'cow'), default='cat', help='choose your companion (default: cat)')
    parser.add_argument('--pet', action='store_true', help='wander between remarks, then walk off after one full monologue')
    parser.add_argument('--loop', action='store_true', help='explicitly opt into repeating the monologue until q')
    parser.add_argument('--demo', action='store_true', help='play the full monologue once (also the default)')
    parser.add_argument('--hold', type=positive, default=3.5, help='seconds to linger after typing (default: 3.5)')
    parser.add_argument('--speed', type=positive, default=160, help='walking speed in pixels/second')
    parser.add_argument('--typing-speed', type=positive, default=32, help='characters per second')
    parser.add_argument('--size', type=int, choices=(180, 270, 360), default=360, help='preferred sprite width in pixels; adapts to small windows')
    parser.add_argument('--fps', type=int, choices=range(12, 61), metavar='12..60', default=30)
    parser.add_argument('--duration', type=positive, help='exit after this many seconds (useful with --pet)')
    args = parser.parse_args(argv)
    if args.loop:
        args.pet = True
    message = ' '.join(args.message)
    if not message and not sys.stdin.isatty():
        message = sys.stdin.read(65536).strip()
    sayings = SAYINGS if args.character == 'cat' else COW_SAYINGS
    messages = [clean(message)] if message.strip() else sayings
    if not sys.stdout.isatty():
        print('\n\n'.join(messages))
        return 0
    try:
        return run(args, messages)
    except KeyboardInterrupt:
        return 130
    except (OSError, RuntimeError) as error:
        print(f'moosay: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
