# encoding: utf-8
from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import tempfile
import six
from contextlib import contextmanager
from mog_commons.unittest import TestCase
from color_ssh import color_ssh
from color_ssh.color_ssh import Setting
from color_ssh.util.util import PY3


class TestSetting(TestCase):
    def _check(self, setting, tasks):
        self.assertEqual(setting.tasks, tasks)
        for _, cmd, setup in setting.tasks:
            self.assertTrue(all(isinstance(c, str) for c in cmd))
            for xs in setup:
                self.assertTrue(all(isinstance(c, str) for c in xs))

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
                    [('server-1', ['ssh', 'server-1', 'pwd'], [])])
        self._check(self._parse(['user@server-1', 'ls', '-l']),
                    [('server-1', ['ssh', 'user@server-1', 'ls', '-l'], [])])

        # label
        self._check(self._parse(['-l', 'label', 'user@server-1', 'ls', '-l']),
                    [('label', ['ssh', 'user@server-1', 'ls', '-l'], [])])
        self._check(self._parse(['--label', 'label', 'user@server-1', 'ls', '-l']),
                    [('label', ['ssh', 'user@server-1', 'ls', '-l'], [])])
        self._check(self._parse(['-llabel', 'user@server-1', 'ls', '-l']),
                    [('label', ['ssh', 'user@server-1', 'ls', '-l'], [])])
        self._check(self._parse(['--label', 'label', '--ssh', '/usr/bin/ssh -v', 'user@server-1', 'ls', '-l']),
                    [('label', ['/usr/bin/ssh', '-v', 'user@server-1', 'ls', '-l'], [])])

        # ssh
        self._check(self._parse(['--ssh', '/usr/bin/ssh -v --option "a b c"', 'user@server-1', 'ls', '-l']),
                    [('server-1', ['/usr/bin/ssh', '-v', '--option', 'a b c', 'user@server-1', 'ls', '-l'], [])])
        self._check(self._parse(['--label', 'あいう'.encode('utf-8'), 'user@server-1', 'ls', '-l']),
                    [('あいう' if PY3 else 'あいう'.encode('utf-8'), ['ssh', 'user@server-1', 'ls', '-l'], [])])
        self._check(self._parse(['--label', b'\xff\xfe', 'user@server-1', 'ls', '-l']),
                    [('\udcff\udcfe' if PY3 else b'\xff\xfe', ['ssh', 'user@server-1', 'ls', '-l'], [])])
        self._check(self._parse(['server-1', 'echo', b'\xff\xfe']),
                    [('server-1', ['ssh', 'server-1', 'echo', '\udcff\udcfe' if PY3 else b'\xff\xfe'], [])])

        # hosts
        hosts_path = os.path.join('tests', 'resources', 'test_color_ssh_hosts.txt')
        self._check(self._parse(['-h', hosts_path, 'pwd']), [
            ('server-1', ['ssh', 'server-1', 'pwd'], []),
            ('server-2', ['ssh', 'server-2', 'pwd'], []),
            ('server-3', ['ssh', 'server-3', 'pwd'], []),
            ('server-4', ['ssh', 'server-4', 'pwd'], []),
            ('server-5', ['ssh', 'server-5', 'pwd'], []),
            ('server-6', ['ssh', 'server-6', 'pwd'], []),
            ('server-7', ['ssh', '-p', '22', 'server-7', 'pwd'], []),
            ('server-8', ['ssh', '-p', '1022', 'server-8', 'pwd'], []),
            ('server-9', ['ssh', 'root@server-9', 'pwd'], []),
            ('server-10', ['ssh', '-p', '1022', 'root@server-10', 'pwd'], []),
        ])
        self._check(self._parse(['-H', 'server-11 root@server-12 root@server-13:1022', 'pwd']), [
            ('server-11', ['ssh', 'server-11', 'pwd'], []),
            ('server-12', ['ssh', 'root@server-12', 'pwd'], []),
            ('server-13', ['ssh', '-p', '1022', 'root@server-13', 'pwd'], []),
        ])
        self._check(self._parse(['--hosts', hosts_path, '--host', 'server-11 root@server-12', 'pwd']), [
            ('server-1', ['ssh', 'server-1', 'pwd'], []),
            ('server-2', ['ssh', 'server-2', 'pwd'], []),
            ('server-3', ['ssh', 'server-3', 'pwd'], []),
            ('server-4', ['ssh', 'server-4', 'pwd'], []),
            ('server-5', ['ssh', 'server-5', 'pwd'], []),
            ('server-6', ['ssh', 'server-6', 'pwd'], []),
            ('server-7', ['ssh', '-p', '22', 'server-7', 'pwd'], []),
            ('server-8', ['ssh', '-p', '1022', 'server-8', 'pwd'], []),
            ('server-9', ['ssh', 'root@server-9', 'pwd'], []),
            ('server-10', ['ssh', '-p', '1022', 'root@server-10', 'pwd'], []),
            ('server-11', ['ssh', 'server-11', 'pwd'], []),
            ('server-12', ['ssh', 'root@server-12', 'pwd'], []),
        ])

        # parallelism
        self.assertEqual(self._parse(['-H', 'server-11 root@server-12', '-p3', 'pwd']).parallelism, 3)
        self.assertEqual(self._parse(['-H', 'server-11 root@server-12', '--par', '15', 'pwd']).parallelism, 15)

        # distribute
        self._check(self._parse(['-H', 'server-11 root@server-12', '--distribute', 'echo "foo bar"', 'x', 'y', 'z']), [
            ('server-11', ['ssh', 'server-11', 'echo', 'foo bar', 'x', 'y'], []),
            ('server-12', ['ssh', 'root@server-12', 'echo', 'foo bar', 'z'], []),
        ])

        # upload
        self._check(
            self._parse([
                '-H', 'server-11 root@server-12', '--distribute', 'echo "foo bar"', '--upload', 'dir1/x', 'dir1/y', 'z'
            ]), [
                ('server-11', ['ssh', 'server-11', 'echo', 'foo bar', 'dir1/x', 'dir1/y'], [
                    ['ssh', 'server-11', 'mkdir', '-p', 'dir1'],
                    ['rsync', '-a', 'dir1/x', 'server-11:dir1/x'],
                    ['rsync', '-a', 'dir1/y', 'server-11:dir1/y']
                ]),
                ('server-12', ['ssh', 'root@server-12', 'echo', 'foo bar', 'z'],
                 [['rsync', '-a', 'z', 'root@server-12:z']]),
            ])

        # upload-with
        self._check(self._parse(['--upload-with=dir1/x', 'server-1', 'pwd']),
                    [('server-1', ['ssh', 'server-1', 'pwd'], [
                        ['ssh', 'server-1', 'mkdir', '-p', 'dir1'],
                        ['rsync', '-a', 'dir1/x', 'server-1:dir1/x'],
                    ])])

        self._check(
            self._parse([
                '--upload-with', 'dir2/c dir2/d dir3/e',
                '-H', 'server-11 root@server-12', '--distribute', 'echo "foo bar"', '--upload', 'dir1/x', 'dir1/y', 'z'
            ]), [
                ('server-11', ['ssh', 'server-11', 'echo', 'foo bar', 'dir1/x', 'dir1/y'], [
                    ['ssh', 'server-11', 'mkdir', '-p', 'dir1', 'dir2', 'dir3'],
                    ['rsync', '-a', 'dir2/c', 'server-11:dir2/c'],
                    ['rsync', '-a', 'dir2/d', 'server-11:dir2/d'],
                    ['rsync', '-a', 'dir3/e', 'server-11:dir3/e'],
                    ['rsync', '-a', 'dir1/x', 'server-11:dir1/x'],
                    ['rsync', '-a', 'dir1/y', 'server-11:dir1/y']
                ]),
                ('server-12', ['ssh', 'root@server-12', 'echo', 'foo bar', 'z'], [
                    ['ssh', 'root@server-12', 'mkdir', '-p', 'dir2', 'dir3'],
                    ['rsync', '-a', 'dir2/c', 'root@server-12:dir2/c'],
                    ['rsync', '-a', 'dir2/d', 'root@server-12:dir2/d'],
                    ['rsync', '-a', 'dir3/e', 'root@server-12:dir3/e'],
                    ['rsync', '-a', 'z', 'root@server-12:z']
                ]),
            ])

    def test_parse_args_error(self):
        with self.withBytesOutput() as (out, err):
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh'], out)
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh', 'server-1'], out)
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh', '--label', 'x'], out)
            self.assertSystemExit(2, Setting().parse_args, ['color-ssh', '--host', '  ', 'pwd'], out)

    def test_parse_host_error(self):
        self.assertRaises(ValueError, Setting._parse_host, '')
        self.assertRaises(ValueError, Setting._parse_host, '@')
        self.assertRaises(ValueError, Setting._parse_host, ':')
        self.assertRaises(ValueError, Setting._parse_host, 'a:')
        self.assertRaises(ValueError, Setting._parse_host, 'a:b')
        self.assertRaises(ValueError, Setting._parse_host, '@a:0')
        self.assertRaises(ValueError, Setting._parse_host, 'a:b@c:0')
        self.assertRaises(ValueError, Setting._parse_host, 'a@@c:0')


class TestMain(TestCase):
    def test_main_single_proc(self):
        # requires: POSIX environment, color-cat command
        def f(bs):
            return b'\x1b[7m\x1b[35mtests/resources/test_color_ssh_01.sh\x1b[0m|\x1b[0m\x1b[35m' + bs + b'\x1b[0m\n'

        def g(bs):
            return b'\x1b[7m\x1b[35mtests/resources/test_color_ssh_01.sh\x1b[0m+\x1b[0m\x1b[35m' + bs + b'\x1b[0m\n'

        with self.__with_temp_output() as (out, err):
            args = ['color-ssh', '--ssh', str('bash'),
                    os.path.join('tests', 'resources', 'test_color_ssh_01.sh'), 'abc', 'def']
            ret = color_ssh.main(args, stdout=out, stderr=err)
            self.assertEqual(ret, 0)

            out.seek(0)
            err.seek(0)

            self.assertEqual(out.read(), f(b'abc') + f(b'foo') + f('あいうえお'.encode('utf-8')) + f(b'\xff\xfe'))
            self.assertEqual(err.read(), g(b'def') + g(b'bar') + g('かきくけこ'.encode('utf-8')) + g(b'\xfd\xfc'))

    def test_main_multi_proc(self):
        # requires: POSIX environment, color-cat command
        def f(bs):
            return b'\x1b[7m\x1b[35mtests/resources/test_color_ssh_01.sh\x1b[0m|\x1b[0m\x1b[35m' + bs + b'\x1b[0m\n'

        def g(bs):
            return b'\x1b[7m\x1b[35mtests/resources/test_color_ssh_01.sh\x1b[0m+\x1b[0m\x1b[35m' + bs + b'\x1b[0m\n'

        with self.__with_temp_output() as (out, err):
            path = os.path.join('tests', 'resources', 'test_color_ssh_01.sh')
            args = ['color-ssh', '--ssh', str('bash'), '-H', '%s %s' % (path, path), 'abc', 'def']

            self.assertFalse(out.closed)
            self.assertFalse(err.closed)

            ret = color_ssh.main(args, stdout=out, stderr=err)
            self.assertEqual(ret, 0)

            out.seek(0)
            err.seek(0)

            self.assertEqual(sorted(out.read()),
                             sorted((f(b'abc') + f(b'foo') + f('あいうえお'.encode('utf-8')) + f(b'\xff\xfe')) * 2))
            self.assertEqual(sorted(err.read()),
                             sorted((g(b'def') + g(b'bar') + g('かきくけこ'.encode('utf-8')) + g(b'\xfd\xfc')) * 2))

    def test_main_load_error(self):
        with self.__with_temp_output() as (out, err):
            args = ['color-ssh', '-h', 'not_exist_file', '--ssh', str('./tests/resources/not_exist_command'), 'x', 'y']
            ret = color_ssh.main(args, stdout=out, stderr=err)
            self.assertEqual(ret, 1)

            out.seek(0)
            err.seek(0)

            self.assertEqual(out.read(), b'')
            self.assertTrue(b'No such file or directory' in err.read())

    def test_main_task_error(self):
        with self.__with_temp_output() as (out, err):
            args = ['color-ssh', '--ssh', str('./tests/resources/not_exist_command'), 'x', 'y']
            ret = color_ssh.main(args, stdout=out, stderr=err)
            self.assertEqual(ret, 1)

            out.seek(0)
            err.seek(0)

            self.assertEqual(out.read(), b'')
            self.assertTrue(b'No such file or directory' in err.read())

    def test_run_task_error(self):
        with self.__with_temp_output() as (out, err):
            ret = color_ssh.run_task(('lab', 'echo x', ['true', 'false']))
            self.assertEqual(ret, 1)

            out.seek(0)
            err.seek(0)

            self.assertEqual(out.read(), b'')
            self.assertTrue(
                b'RuntimeError: Failed to execute setup command: false\nlabel=lab, command=echo x\n' in err.read())

    @staticmethod
    @contextmanager
    def __with_temp_output():
        with tempfile.TemporaryFile() as out:
            with tempfile.TemporaryFile() as err:
                old_stdout = sys.stdout
                old_stderr = sys.stderr

                try:
                    try:
                        sys.stdout.buffer = out
                        sys.stderr.buffer = err
                    except AttributeError:
                        sys.stdout = out
                        sys.stderr = err

                    yield out, err
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
