import base64
import fcntl
import os
from pathlib import Path
import pty
import re
import select
import signal
import struct
import subprocess
import sys
import termios
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import catsay


class TextTests(unittest.TestCase):
    def test_unicode_long_words_and_multiline_pagination(self):
        text = 'Hello 界界界 café\n' + 'x'*130 + '\nlast line'
        pages = catsay.pages([text], 14, 2)
        self.assertGreater(len(pages), 3)
        self.assertTrue(all(catsay.width(line) <= 14 for page in pages for line in page.split('\n')))
        self.assertTrue(all(len(page.split('\n')) <= 2 for page in pages))

    def test_controls_cannot_escape_into_terminal(self):
        self.assertNotIn('\x1b', catsay.clean('hey\x1b[2J'))
        self.assertNotIn('\x07', catsay.clean('ding\x07'))

    def test_upload_preserves_image_and_limits_chunks(self):
        data = os.urandom(13000)
        commands = catsay.upload(data, 42).split(b'\x1b\\')[:-1]
        payloads = [command.split(b';', 1)[1] for command in commands]
        self.assertTrue(all(len(p) <= 4096 for p in payloads))
        self.assertEqual(base64.b64decode(b''.join(payloads)), data)
        self.assertIn(b'm=0;', commands[-1])

    def test_all_bundled_poses_are_valid_png_at_expected_dimensions(self):
        for size in (180, 270, 360):
            paths = list((catsay.ASSETS/str(size)).glob('*.png'))
            self.assertEqual(len(paths), 72)
            for path in paths:
                data = path.read_bytes()
                self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack('>II', data[16:24]), (size, round(size*260/360)))

    def test_pipe_output(self):
        result = subprocess.run([sys.executable, 'catsay.py'], input='Hello terminal', text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout, 'Hello terminal\n')

    def test_no_message_shows_help_even_with_previous_pet_alias(self):
        for args in ([], ['--pet']):
            result = subprocess.run([sys.executable, 'catsay.py', *args], input='', text=True, capture_output=True, check=True)
            self.assertIn('usage: catsay', result.stdout)
            self.assertIn('--yarn', result.stdout)
            self.assertNotIn('--character', result.stdout)


class TerminalTests(unittest.TestCase):
    def exercise(self, *, support=True, terminate=False, small=False, whole_show=False, play=None):
        master, slave = pty.openpty()
        original = termios.tcgetattr(slave)
        def resize(rows, cols):
            fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, cols*10, rows*20))
        resize(16, 36) if small else resize(30, 100)
        def setup():
            os.setsid()
            fcntl.ioctl(0, termios.TIOCSCTTY, 0)
        args = ['--pet', '--speed', '20000', '--hold', '.09', '--typing-speed', '10000', 'Hello from the cat.'] if whole_show else ['--pet', '--duration', '1.3', '--speed', '2000', 'Hello cat']
        if play:
            args = [play, '--duration', '1.3', '--speed', '2000']
        command = [sys.executable, 'catsay.py', *args]
        if play == '--steal':
            command = [sys.executable, '-c', 'import playground, catsay; playground.capture_screen = lambda: ["hello terminal", "letters for the cat", "third row"]; raise SystemExit(catsay.main(' + repr(args) + '))']
        child = subprocess.Popen(command, stdin=slave, stdout=slave, stderr=slave, preexec_fn=setup)
        output = bytearray()
        answered = changed = False
        deadline = time.monotonic()+12
        try:
            while time.monotonic() < deadline:
                if select.select([master], [], [], .05)[0]:
                    output.extend(os.read(master, 65536))
                if not answered and b'a=q' in output:
                    if support:
                        os.write(master, b'\x1b_Gi=918273;OK\x1b\\')
                    answered = True
                if not changed and b'a=p' in output:
                    if terminate:
                        child.send_signal(signal.SIGTERM)
                    else:
                        resize(24, 70)
                    changed = True
                if child.poll() is not None:
                    while select.select([master], [], [], .05)[0]:
                        output.extend(os.read(master, 65536))
                    break
            self.assertIsNotNone(child.poll(), 'animation did not exit on time')
            self.assertEqual(termios.tcgetattr(slave), original)
            if play and play != '--steal':
                self.assertNotIn(b'\x1b[2J', output)
                self.assertNotIn(b'\x1b[2K', output)
                self.assertNotIn(b'\x1b[?1049h', output)
                self.assertIn(b'\x1b8\x1b[?25h', output)
            else:
                self.assertIn(b'\x1b[?25h\x1b[?1049l', output)
            if play == '--steal':
                self.assertIn(b'letters for the cat', output)
            self.assertNotIn(b'Traceback', output)
            if whole_show:
                self.assertIn(b'Hello from the cat.', output)
            if support:
                self.assertIn(b'a=p', output)
                self.assertIn(b'd=I', output)
                cached_images = set()
                for command in re.finditer(rb'\x1b_G([^;]*);[^\x1b]*\x1b\\|\x1b\[2J', output):
                    if command.group(1) is None:
                        cached_images.clear()
                        continue
                    fields = dict(part.split(b'=', 1) for part in command.group(1).split(b',') if b'=' in part)
                    image_id = fields.get(b'i')
                    if fields.get(b'a') == b't':
                        cached_images.add(image_id)
                    elif fields.get(b'a') == b'p':
                        self.assertIn(image_id, cached_images, 'placement refers to image erased by a screen clear')
                    elif fields.get(b'd') == b'I':
                        cached_images.discard(image_id)
                self.assertEqual(child.returncode, 130 if terminate else 0)
            else:
                self.assertEqual(child.returncode, 1)
                self.assertIn(b'did not answer', output)
        finally:
            if child.poll() is None:
                child.kill()
            child.wait()
            os.close(master)
            os.close(slave)

    def test_animation_resize_and_cleanup(self):
        self.exercise()

    def test_custom_message_exits_without_time_limit(self):
        self.exercise(whole_show=True)

    def test_sigterm_restores_terminal(self):
        self.exercise(terminate=True)

    def test_small_window(self):
        self.exercise(small=True)

    def test_unsupported_terminal(self):
        self.exercise(support=False)

    def test_play_modes_preserve_underlying_screen(self):
        for mode in ('--overlay', '--yarn', '--laser', '--zoomies', '--steal'):
            with self.subTest(mode=mode):
                self.exercise(play=mode)

    def test_overlay_sigterm_restores_cursor_and_input(self):
        self.exercise(play='--yarn', terminate=True)


if __name__ == '__main__':
    unittest.main()
