# encoding: utf-8
from __future__ import division, print_function, absolute_import, unicode_literals

import os
import io
import sys
import tempfile
import six
from mog_commons.unittest import TestCase
from color_ssh import color_ssh
from color_ssh.color_ssh import Setting
from color_ssh.util.util import PY3


class TestSetting(TestCase):
    def _check(self, setting, expected):
        self.assertEqual(setting.label, expected.label)
        self.assertEqual(setting.command, expected.command)

    def _parse(self, args):
        xs = []
        for arg in ['color-ssh'] + args:
            if six.PY2 and isinstance(arg, unicode):
                xs.append(arg.encode('utf-8'))
            elif six.PY3 and isinstance(arg, bytes):
                xs.append(os.fsdecode(arg))
            else:
                xs.append(arg)
        return Setting().parse_args(xs)

    def test_parse_args(self):
        self._check(self._parse(['server-1', 'pwd']),
                    Setting('server-1', ['ssh', 'server-1', 'pwd']))
        self._check(self._parse(['user@server-1', 'ls', '-l']),
                    Setting('server-1', ['ssh', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['-l', 'label', 'user@server-1', 'ls', '-l']),
                    Setting('label', ['ssh', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['--label', 'label', 'user@server-1', 'ls', '-l']),
                    Setting('label', ['ssh', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['-llabel', 'user@server-1', 'ls', '-l']),
                    Setting('label', ['ssh', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['--label', 'label', '--ssh', '/usr/bin/ssh -v', 'user@server-1', 'ls', '-l']),
                    Setting('label', ['/usr/bin/ssh', '-v', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['--ssh', '/usr/bin/ssh -v --option "a b c"', 'user@server-1', 'ls', '-l']),
                    Setting('server-1', ['/usr/bin/ssh', '-v', '--option', 'a b c', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['--label', 'あいう'.encode('utf-8'), 'user@server-1', 'ls', '-l']),
                    Setting('あいう' if PY3 else 'あいう'.encode('utf-8'), ['ssh', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['--label', b'\xff\xfe', 'user@server-1', 'ls', '-l']),
                    Setting('\udcff\udcfe' if PY3 else b'\xff\xfe', ['ssh', 'user@server-1', 'ls', '-l']))
        self._check(self._parse(['server-1', 'echo', b'\xff\xfe']),
                    Setting('server-1', ['ssh', 'server-1', 'echo', '\udcff\udcfe' if PY3 else b'\xff\xfe']))

    def test_parse_args_error(self):
        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh'], out)
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh', 'server-1'], out)
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh', '--label', 'x'], out)


class TestMain(TestCase):
    def test_main(self):
        # requires: POSIX environment, color-cat command
        def f(bs):
            return b'\x1b[7m\x1b[35mtests/resources/test_color_ssh_01.sh\x1b[0m|\x1b[0m\x1b[35m' + bs + b'\n\x1b[0m'

        def g(bs):
            return b'\x1b[7m\x1b[35mtests/resources/test_color_ssh_01.sh\x1b[0m+\x1b[0m\x1b[35m' + bs + b'\n\x1b[0m'

        with tempfile.TemporaryFile() as out:
            with tempfile.TemporaryFile() as err:
                args = ['color-ssh', '--ssh', str('bash'),
                        os.path.join('tests', 'resources', 'test_color_ssh_01.sh'), 'abc', 'def']
                ret = color_ssh.main(args, stdout=out, stderr=err)
                self.assertEqual(ret, 0)

                out.seek(0)
                err.seek(0)

                self.assertEqual(out.read(), f(b'abc') + f(b'foo') + f('あいうえお'.encode('utf-8')) + f(b'\xff\xfe'))
                self.assertEqual(err.read(), g(b'def') + g(b'bar') + g('かきくけこ'.encode('utf-8')) + g(b'\xfd\xfc'))

    def test_main_error(self):
        with tempfile.TemporaryFile() as out:
            with tempfile.TemporaryFile() as err:
                args = ['color-ssh', '--ssh', str('./tests/resources/not_exist_command'), 'x', 'y']
                ret = color_ssh.main(args, stdout=out, stderr=err)
                self.assertEqual(ret, 1)

                out.seek(0)
                err.seek(0)

                self.assertEqual(out.read(), b'')
                self.assertTrue(b'No such file or directory' in err.read())
