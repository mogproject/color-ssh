# encoding: utf-8
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import six
from mog_commons.unittest import TestCase
from color_ssh import color_cat
from color_ssh.color_cat import Setting


class TestSetting(TestCase):
    def _check(self, setting, expected):
        self.assertEqual(setting.prefix, expected.prefix)
        self.assertEqual(setting.paths, expected.paths)

    def _parse(self, args):
        xs = []
        for arg in ['color-cat'] + args:
            if six.PY2 and isinstance(arg, unicode):
                xs.append(arg.encode('utf-8'))
            elif six.PY3 and isinstance(arg, bytes):
                xs.append(os.fsdecode(arg))
            else:
                xs.append(arg)
        return Setting().parse_args(xs)

    def test_parse_args(self):
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
            self.assertSystemExit(2, Setting().parse_args, ['color-cat', '-l', '1', '-c', 'xxx'], out)
        self.assertEqual(out.getvalue().split(b'\n')[0], b'Usage: setup.py [options...] [file ...]')
        self.assertEqual(out.getvalue().split(b'\n')[-2], b'Invalid color name: xxx')
        self.assertEqual(err.getvalue(), b'')

        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args,
                                  ['color-cat', '-l', '1', '-c', 'あいう'.encode('utf-8')], out)
        self.assertEqual(out.getvalue().split(b'\n')[0], b'Usage: setup.py [options...] [file ...]')
        self.assertEqual(out.getvalue().split(b'\n')[-2], 'Invalid color name: あいう'.encode('utf-8'))
        self.assertEqual(err.getvalue(), b'')

        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args, ['color-cat', '-l', '1', '-c', b'\xff\xfe'], out)
        self.assertEqual(out.getvalue().split(b'\n')[0], b'Usage: setup.py [options...] [file ...]')
        self.assertEqual(out.getvalue().split(b'\n')[-2], b'Invalid color name: \xff\xfe')
        self.assertEqual(err.getvalue(), b'')


class TestMain(TestCase):
    def test_main(self):
        with self.withBytesOutput() as (out, err):
            args = ['color-cat',
                    os.path.join('tests', 'resources', 'test_01.txt'),
                    os.path.join('tests', 'resources', 'test_02.txt')]
            ret = color_cat.main(args, stdout=out, stderr=err)
            self.assertEqual(ret, 0)
        self.assertEqual(out.getvalue(),
                         b'\x1b[31mfoo\n\x1b[0m\x1b[31mbar\n\x1b[0m\x1b[31mbaz\n\x1b[0m'
                         b'\x1b[31m123\n\x1b[0m\x1b[31m456\n\x1b[0m\x1b[31m789\n\x1b[0m')
        self.assertEqual(err.getvalue(), b'')

    def test_main_error(self):
        with self.withBytesOutput() as (out, err):
            args = ['color-cat', os.path.join('tests', 'resources', 'test_01_not_exist.txt')]
            ret = color_cat.main(args, stdout=out, stderr=err)
            self.assertEqual(ret, 1)
        self.assertEqual(out.getvalue(), b'')
        self.assertTrue(b'No such file or directory' in err.getvalue())
