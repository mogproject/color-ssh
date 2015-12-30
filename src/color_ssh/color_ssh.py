from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import io
import shlex
import subprocess
import re
from optparse import OptionParser
from multiprocessing.pool import Pool
from color_ssh.util.util import *

__all__ = []


class Setting(object):
    VERSION = 'color-ssh %s' % __import__('color_ssh').__version__
    USAGE = '\n'.join([
        '%prog [options...] [user@]hostname command',
        '       %prog [options...] -h host_file command',
        '       %prog [options...] -H "[user@]hostname [[user@]hostname]...]" command'
    ])
    DEFAULT_PARALLELISM = 32
    CMD_SSH = str('ssh')
    CMD_UPLOAD = [str('rsync'), str('-a')]
    CMD_MKDIR = [str('mkdir'), str('-p')]

    def __init__(self, parallelism=None, tasks=None):
        self.parallelism = parallelism
        self.tasks = tasks

    def parse_args(self, argv, stdout=io2bytes(sys.stdout)):
        """
        :param argv: list of str
        :param stdout: binary-data stdout output
        """
        parser = OptionParser(version=self.VERSION, usage=self.USAGE, conflict_handler='resolve')
        parser.allow_interspersed_args = False

        parser.add_option(
            '-l', '--label', dest='label', default=None, type='string', metavar='LABEL',
            help='label name'
        )
        parser.add_option(
            '--ssh', dest='ssh', default=self.CMD_SSH, type='string', metavar='SSH',
            help='override ssh command line string'
        )
        parser.add_option(
            '-h', '--hosts', dest='host_file', default=None, type='string', metavar='HOST_FILE',
            help='hosts file (each line "[user@]host")'
        )
        parser.add_option(
            '-H', '--host', dest='host_string', default=None, type='string', metavar='HOST_STRING',
            help='additional host entries ("[user@]host")'
        )
        parser.add_option(
            '-p', '--par', dest='parallelism', default=self.DEFAULT_PARALLELISM, type='int', metavar='PAR',
            help='max number of parallel threads (default: %d)' % self.DEFAULT_PARALLELISM
        )
        parser.add_option(
            '--distribute', dest='distribute', default=None, type='string', metavar='PREFIX',
            help='split and distribute command-line arguments to each host'
        )
        parser.add_option(
            '--upload', dest='upload', default=False, action='store_true',
            help='upload files before executing a command (all args are regarded as paths)'
        )
        parser.add_option(
            '--upload-with', dest='upload_with', default=None, type='string', metavar='PATH',
            help='file paths to be uploaded before executing a command'
        )

        option, args = parser.parse_args(argv[1:])
        hosts = self._load_hosts(option.host_file) + (option.host_string.split() if option.host_string else [])

        if len(args) < (1 if hosts else 2):
            print(option.__dict__)
            stdout.write(arg2bytes(parser.format_help().encode('utf-8')))
            parser.exit(2)

        if not hosts:
            hosts = args[:1]
            del args[0]

        # parse hosts
        parsed_hosts = [self._parse_host(h) for h in hosts]

        # parse upload-with option
        upload_with = [] if option.upload_with is None else shlex.split(option.upload_with)

        tasks = []
        if option.distribute:
            # distribute args
            dist_prefix = shlex.split(option.distribute)
            d = distribute(len(hosts), args)
            for i, (user, host, port) in enumerate(parsed_hosts):
                if d[i]:
                    upload_paths = upload_with + d[i] if option.upload else []
                    label = option.label or host
                    ssh_args = self._ssh_args(option.ssh, user, host, port)
                    tasks.append((label, ssh_args + dist_prefix + d[i],
                                  self._build_upload_commands(user, host, port, option.ssh, upload_paths)))
        else:
            for user, host, port in parsed_hosts:
                tasks.append((option.label or host,
                              self._ssh_args(option.ssh, user, host, port) + args,
                              self._build_upload_commands(user, host, port, option.ssh, upload_with)))

        self.parallelism = option.parallelism
        self.tasks = tasks
        return self

    @staticmethod
    def _load_hosts(path):
        if not path:
            return []

        with io.open(path) as f:
            lines = f.readlines()
        return list(filter(lambda x: str(x), (line.strip() for line in lines)))

    @staticmethod
    def _parse_host(s):
        """
        :param s: string : [user@]host[:port]
        :return: tuple of (user, host, port)
        """
        ret = re.match('^(?:([^:@]+)@)?([^:@]+)(?::(\d+))?$', s)
        if not ret:
            raise ValueError('Illegal format: %s' % s)
        return [None if s is None else str(s) for s in ret.groups()]

    @staticmethod
    def _build_host_string(user, host):
        ret = host
        if user:
            ret = ('%s@' % user) + ret
        return str(ret)

    @staticmethod
    def _ssh_args(ssh_cmd, user, host, port):
        return shlex.split(ssh_cmd) + (
            [] if port is None else [str('-p'), port]) + [Setting._build_host_string(user, host)]

    @staticmethod
    def _upload_args(user, host, port, path):
        return Setting.CMD_UPLOAD + ([] if port is None else [str('-P'), port]) + [
            path,
            Setting._build_host_string(user, host) + str(':') + path
        ]

    @staticmethod
    def _build_upload_commands(user, host, port, ssh_cmd, paths):
        # create directories
        dirs = list(set(x for x in [os.path.dirname(path) for path in paths] if x != '' and x != '.'))

        ret = []
        if dirs:
            ret.append(Setting._ssh_args(ssh_cmd, user, host, port) + Setting.CMD_MKDIR + sorted(dirs))

        # upload files
        ret.extend([Setting._upload_args(user, host, port, path) for path in paths])
        return ret


def run_task(args):
    label, command, setup_commands = args

    # We don't pass stdout/stderr file descriptors since this function runs in the forked processes.
    stdout = io2bytes(sys.stdout)
    stderr = io2bytes(sys.stderr)

    prefix = ['color-cat', '-l', label]

    def exc_func(e):
        msg = '%s: %s\nlabel=%s, command=%s\n' % (e.__class__.__name__, e, label, command)
        stderr.write(msg.encode('utf-8', 'ignore'))

    @exception_handler(exc_func)
    def f():
        proc_stdout = subprocess.Popen(prefix, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        proc_stderr = subprocess.Popen(prefix + ['-s', '+'], stdin=subprocess.PIPE, stdout=stderr, stderr=stderr)

        for cmd in setup_commands:
            proc_stderr.stdin.write(('setup: %s\n' % cmd).encode('utf-8', 'ignore'))

            r = subprocess.call(cmd, stdin=None, stdout=proc_stdout.stdin, stderr=proc_stderr.stdin)
            if r != 0:
                raise RuntimeError('Failed to execute setup command: %s' % cmd)

        ret = subprocess.call(command, stdin=None, stdout=proc_stdout.stdin, stderr=proc_stderr.stdin)

        proc_stdout.stdin.close()
        proc_stderr.stdin.close()

        proc_stdout.wait()
        proc_stderr.wait()
        return ret

    return f()


def main(argv=sys.argv, stdout=io2bytes(sys.stdout), stderr=io2bytes(sys.stderr)):
    """
    Main function
    """

    @exception_handler(lambda e: stderr.write(('%s: %s\n' % (e.__class__.__name__, e)).encode('utf-8', 'ignore')))
    def f():
        setting = Setting().parse_args(argv, stdout)
        n = min(len(setting.tasks), setting.parallelism)
        if n <= 1:
            ret = map(run_task, setting.tasks)
        else:
            pool = Pool(n)
            ret = pool.map(run_task, setting.tasks)
        return max(ret)

    return f()
