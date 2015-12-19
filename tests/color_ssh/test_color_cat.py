# encoding: utf-8
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import sys
import six
from mog_commons.unittest import TestCase
from color_ssh.color_cat import Setting


class TestSetting(TestCase):
    def _check(self, setting, expected):
        self.assertEqual(setting.prefix, expected.prefix)
        self.assertEqual(setting.paths, expected.paths)

    def _parse(self, args):
        xs = []
        for arg in args:
            if six.PY2 and isinstance(arg, unicode):
                xs.append(arg.encode('utf-8'))
            elif six.PY3 and isinstance(arg, bytes):
                xs.append(os.fsdecode(arg))
            else:
                xs.append(arg)
        return Setting().parse_args(sys.stdout, ['color-cat' if six.PY3 else b'color-cat'] + xs)

    def test_parse_args_py2(self):
        self._check(self._parse([]), Setting(b'\x1b[31m', [None]))
        self._check(self._parse(['']), Setting(b'\x1b[31m', [b'']))
        self._check(self._parse(['a', 'b', 'c', 'd', 'e']),
                    Setting(b'\x1b[31m', [b'a', b'b', b'c', b'd', b'e']))

        # non-ASCII args
        self._check(self._parse(['あいう', 'えお']),
                    Setting(b'\x1b[31m', ['あいう'.encode('utf-8'), 'えお'.encode('utf-8')]))
        self._check(self._parse([b'\xff', b'\xfe']), Setting(b'\x1b[31m', [b'\xff', b'\xfe']))

        # labels
        self._check(self._parse(['-l', '1']),
                    Setting(b'\x1b[7m\x1b[31m1\x1b[0m|\x1b[0m\x1b[31m', [None]))
        self._check(self._parse(['--label', '1']),
                    Setting(b'\x1b[7m\x1b[31m1\x1b[0m|\x1b[0m\x1b[31m', [None]))
        self._check(self._parse(['-l', '2']),
                    Setting(b'\x1b[7m\x1b[32m2\x1b[0m|\x1b[0m\x1b[32m', [None]))
        self._check(self._parse(['-l', '3']),
                    Setting(b'\x1b[7m\x1b[33m3\x1b[0m|\x1b[0m\x1b[33m', [None]))
        self._check(self._parse(['-l', '4']),
                    Setting(b'\x1b[7m\x1b[34m4\x1b[0m|\x1b[0m\x1b[34m', [None]))
        self._check(self._parse(['-l', '5']),
                    Setting(b'\x1b[7m\x1b[35m5\x1b[0m|\x1b[0m\x1b[35m', [None]))
        self._check(self._parse(['-l', '6']),
                    Setting(b'\x1b[7m\x1b[36m6\x1b[0m|\x1b[0m\x1b[36m', [None]))
        self._check(self._parse(['-l', '7']),
                    Setting(b'\x1b[7m\x1b[37m7\x1b[0m|\x1b[0m\x1b[37m', [None]))
        self._check(self._parse(['-l', '8']),
                    Setting(b'\x1b[7m\x1b[31m8\x1b[0m|\x1b[0m\x1b[31m', [None]))
        self._check(self._parse(['-l', '11111111']),
                    Setting(b'\x1b[7m\x1b[31m11111111\x1b[0m|\x1b[0m\x1b[31m', [None]))
        self._check(self._parse(['-l', 'あいう']),
                    Setting(b'\x1b[7m\x1b[32m\xe3\x81\x82\xe3\x81\x84\xe3\x81\x86\x1b[0m|\x1b[0m\x1b[32m', [None]))
        self._check(self._parse(['-l', b'\xff\xfe']),
                    Setting(b'\x1b[7m\x1b[36m\xff\xfe\x1b[0m|\x1b[0m\x1b[36m', [None]))

        # colors
        self._check(self._parse(['-c', 'blue']),
                    Setting(b'\x1b[34m', [None]))
        self._check(self._parse(['-l', '1', '-c', 'blue']),
                    Setting(b'\x1b[7m\x1b[34m1\x1b[0m|\x1b[0m\x1b[34m', [None]))
        self._check(self._parse(['-l', '1', '--color', 'Yellow']),
                    Setting(b'\x1b[7m\x1b[33m1\x1b[0m|\x1b[0m\x1b[33m', [None]))

        # separators
        self._check(self._parse(['-s', '+']), Setting(b'\x1b[31m', [None]))
        self._check(self._parse(['-l', 'abc', '-s', '+']),
                    Setting(b'\x1b[7m\x1b[31mabc\x1b[0m+\x1b[0m\x1b[31m', [None]))
        self._check(self._parse(['--label', 'abc', 'xyz', '--separator', 'def', 'ghi', '--color', 'CYAN', 'jkl']),
                    Setting(b'\x1b[7m\x1b[36mabc\x1b[0mdef\x1b[0m\x1b[36m', [b'xyz', b'ghi', b'jkl']))
        self._check(self._parse(['-l', 'abc', '-s', 'あいう']),
                    Setting(b'\x1b[7m\x1b[31mabc\x1b[0m' + 'あいう'.encode('utf-8') + b'\x1b[0m\x1b[31m', [None]))
        self._check(self._parse(['-l', 'abc', '-s', b'\xff\xfe']),
                    Setting(b'\x1b[7m\x1b[31mabc\x1b[0m\xff\xfe\x1b[0m\x1b[31m', [None]))

    def test_parse_args_error(self):
        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args, out, ['color-cat', '-l', '1', '-c', 'xxx'])
        self.assertEqual(out.getvalue().split(b'\n', 3)[:3],
                         [b'Invalid color name: xxx', b'', b'Usage: setup.py [options...] [file ...]'])
        self.assertEqual(err.getvalue(), b'')

        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args, out,
                                  ['color-cat', '-l', '1', '-c', 'あいう'.encode('utf-8')])
        self.assertEqual(out.getvalue().split(b'\n', 3)[:3],
                         ['Invalid color name: あいう'.encode('utf-8'), b'', b'Usage: setup.py [options...] [file ...]'])
        self.assertEqual(err.getvalue(), b'')

        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args, out, ['color-cat', '-l', '1', '-c', b'\xff\xfe'])
        self.assertEqual(out.getvalue().split(b'\n', 3)[:3],
                         [b'Invalid color name: \xff\xfe', b'', b'Usage: setup.py [options...] [file ...]'])
        self.assertEqual(err.getvalue(), b'')
