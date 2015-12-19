from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import shlex
import subprocess
from optparse import OptionParser

PY3 = sys.version_info >= (3,)

__all__ = []


def _io2bytes(fd):
    return fd.buffer if PY3 else fd


class Setting(object):
    VERSION = 'color-ssh %s' % __import__('color_ssh').__version__
    USAGE = """%prog [options...] [user@]hostname command"""

    def __init__(self, label=None, command=None):
        self.label = label
        self.command = command

    def parse_args(self, argv):
        parser = OptionParser(version=self.VERSION, usage=self.USAGE)
        parser.allow_interspersed_args = False

        parser.add_option(
            '-l', '--label', dest='label', default=None, type='string', metavar='LABEL',
            help='set label name to LABEL'
        )
        parser.add_option(
            '--ssh', dest='ssh', default='ssh', type='string', metavar='SSH',
            help='override ssh command line string to SSH'
        )

        option, args = parser.parse_args(argv[1:])

        if len(args) < 2:
            parser.print_help()
            parser.exit(2)

        self.label = option.label or args[0].rsplit('@', 1)[-1]
        self.command = shlex.split(option.ssh) + args
        return self


def main(argv=sys.argv, stdin=_io2bytes(sys.stdin), stdout=_io2bytes(sys.stdout), stderr=_io2bytes(sys.stderr)):
    """
    Main function
    """
    setting = Setting().parse_args(argv)

    try:
        proc_stdout = subprocess.Popen(
            ['color-cat', '-l', setting.label], stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        proc_stderr = subprocess.Popen(
            ['color-cat', '-l', setting.label, '-s', '+'], stdin=subprocess.PIPE, stdout=stderr, stderr=stderr)
        ret = subprocess.call(setting.command, stdin=stdin, stdout=proc_stdout.stdin, stderr=proc_stderr.stdin)

    except Exception as e:
        msg = '%s: %s\nCommand: %s\n' % (e.__class__.__name__, e, setting.command)
        stderr.write(msg.encode('utf-8', 'ignore'))
        return 1

    return ret
