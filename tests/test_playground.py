import unittest

import playground


class ScreenTests(unittest.TestCase):
    def test_snapshot_keeps_color_but_cannot_execute_terminal_commands(self):
        text = '\x1b[31mhello\x1b[0m\x1b[2J\x1b]52;c;clipboard\x07\x1bPpayload\x1b\\'
        self.assertEqual(playground.safe_line(text), '\x1b[31mhello\x1b[0m')

    def test_words_after_wide_characters_use_terminal_cell_positions(self):
        self.assertEqual(playground.screen_words(['\x1b[31m界 hello\x1b[0m'], 80, 24), [(1, 4, 'hello')])

    def test_stealing_changes_copy_and_keeps_other_lines(self):
        lines = ['hello terminal', 'untouched']
        out = playground.repaint(lines, 24, 80, (1, 7, 'terminal'), 3)
        self.assertIn('untouched', out)
        self.assertIn('\x1b[1;7H\x1b[0m   ', out)
        self.assertEqual(lines, ['hello terminal', 'untouched'])
