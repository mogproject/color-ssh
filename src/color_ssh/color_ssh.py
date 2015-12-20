from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import io
import shlex
import subprocess
from optparse import OptionParser
from color_ssh.util.util import *
from multiprocessing.pool import Pool

__all__ = []


class Setting(object):
    VERSION = 'color-ssh %s' % __import__('color_ssh').__version__
    USAGE = '\n'.join([
        '%prog [options...] [user@]hostname command',
        '       %prog [options...] -h host_file command',
        '       %prog [options...] -H "[user@]hostname [[user@]hostname]...]" command'
    ])
    DEFAULT_PARALLELISM = 32

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
            '--ssh', dest='ssh', default=str('ssh'), type='string', metavar='SSH',
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

        option, args = parser.parse_args(argv[1:])
        hosts = self._load_hosts(option.host_file) + (option.host_string.split() if option.host_string else [])

        if len(args) < (1 if hosts else 2):
            stdout.write(arg2bytes(parser.format_help().encode('utf-8')))
            parser.exit(2)

        prefix = shlex.split(option.ssh)

        if not hosts:
            hosts = args[:1]
            command = args[1:]
        else:
            command = args

        tasks = [(option.label or self._extract_label(host), prefix + [host] + command) for host in hosts]

        self.parallelism = option.parallelism
        self.tasks = tasks
        return self

    @staticmethod
    def _load_hosts(path):
        if not path:
            return []

        with io.open(path) as f:
            lines = f.readlines()
        return list(filter(lambda x: x, (line.strip() for line in lines)))

    @staticmethod
    def _extract_label(host):
        return host.rsplit('@', 1)[-1]


def run_task(args):
    label, command = args

    # We don't pass stdout/stderr file descriptors since this function runs in the forked processes.
    stdout = io2bytes(sys.stdout)
    stderr = io2bytes(sys.stderr)

    prefix = ['color-cat', '-l', label]

    try:
        proc_stdout = subprocess.Popen(prefix, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        proc_stderr = subprocess.Popen(prefix + ['-s', '+'], stdin=subprocess.PIPE, stdout=stderr, stderr=stderr)
        ret = subprocess.call(command, stdin=None, stdout=proc_stdout.stdin, stderr=proc_stderr.stdin)

        proc_stdout.stdin.close()
        proc_stderr.stdin.close()

        proc_stdout.wait()
        proc_stderr.wait()
    except Exception as e:
        msg = '%s: %s\nlabel=%s, command=%s\n' % (e.__class__.__name__, e, label, command)
        stderr.write(msg.encode('utf-8', 'ignore'))
        return 1
    return ret


def main(argv=sys.argv, stdout=io2bytes(sys.stdout), stderr=io2bytes(sys.stderr)):
    """
    Main function
    """

    try:
        setting = Setting().parse_args(argv, stdout)
        n = min(len(setting.tasks), setting.parallelism)
        if n <= 1:
            ret = map(run_task, setting.tasks)
        else:
            pool = Pool(n)
            ret = pool.map(run_task, setting.tasks)
    except Exception as e:
        msg = '%s: %s\n' % (e.__class__.__name__, e)
        stderr.write(msg.encode('utf-8', 'ignore'))
        return 1

    return max(ret)
