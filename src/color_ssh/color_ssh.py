from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import shlex
import subprocess
from optparse import OptionParser
from color_ssh.util.util import *

__all__ = []


class Setting(object):
    VERSION = 'color-ssh %s' % __import__('color_ssh').__version__
    USAGE = """%prog [options...] [user@]hostname command"""

    def __init__(self, label=None, command=None):
        self.label = label
        self.command = command

    def parse_args(self, argv, stdout=io2bytes(sys.stdout)):
        """
        :param argv: list of str
        :param stdout: binary-data stdout output
        """
        parser = OptionParser(version=self.VERSION, usage=self.USAGE)
        parser.allow_interspersed_args = False

        parser.add_option(
            '-l', '--label', dest='label', default=None, type='string', metavar='LABEL',
            help='set label name to LABEL'
        )
        parser.add_option(
            '--ssh', dest='ssh', default=str('ssh'), type='string', metavar='SSH',
            help='override ssh command line string to SSH'
        )

        option, args = parser.parse_args(argv[1:])

        if len(args) < 2:
            stdout.write(arg2bytes(parser.format_help().encode('utf-8')))
            parser.exit(2)

        self.label = option.label or args[0].rsplit('@', 1)[-1]
        self.command = shlex.split(option.ssh) + args
        return self


def main(argv=sys.argv, stdin=io2bytes(sys.stdin), stdout=io2bytes(sys.stdout), stderr=io2bytes(sys.stderr)):
    """
    Main function
    """
    setting = Setting().parse_args(argv)
    prefix = ['color-cat', '-l', setting.label]

    try:
        proc_stdout = subprocess.Popen(prefix, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        proc_stderr = subprocess.Popen(prefix + ['-s', '+'], stdin=subprocess.PIPE, stdout=stderr, stderr=stderr)
        ret = subprocess.call(setting.command, stdin=stdin, stdout=proc_stdout.stdin, stderr=proc_stderr.stdin)

        proc_stdout.stdin.close()
        proc_stderr.stdin.close()

        proc_stdout.wait()
        proc_stderr.wait()

    except Exception as e:
        msg = '%s: %s\nCommand: %s\n' % (e.__class__.__name__, e, setting.command)
        stderr.write(msg.encode('utf-8', 'ignore'))
        return 1

    return ret
