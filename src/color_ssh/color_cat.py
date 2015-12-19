from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import io
from optparse import OptionParser
from color_ssh.setting.color import *

PY3 = sys.version_info >= (3,)

__all__ = []


def _arg2bytes(arg):
    return os.fsencode(arg) if PY3 else arg


def _io2bytes(fd):
    return fd.buffer if PY3 else fd


class Setting(object):
    VERSION = 'color-cat %s' % __import__('color_ssh').__version__
    USAGE = """%prog [options...] [file ...]"""

    def __init__(self, prefix=None, paths=None):
        self.prefix = prefix
        self.paths = paths

    def parse_args(self, stdout, argv):
        """
        :param stdout: binary-data stdout output
        :param argv: list of str
        """
        parser = OptionParser(version=self.VERSION, usage=self.USAGE)

        parser.add_option(
            '-l', '--label', dest='label', default=b'', type='string', metavar='LABEL',
            help='set label name to LABEL'
        )
        parser.add_option(
            '-c', '--color', dest='color', default=None, type='string', metavar='COLOR',
            help='set output color to COLOR (available colors: %s)' % ', '.join(sorted(COLOR_NAMES.keys()))
        )
        parser.add_option(
            '-s', '--separator', dest='separator', default=b'|', type='string', metavar='SEPARATOR',
            help='set separator string to SEPARATOR (default: "|")'
        )

        option, args = parser.parse_args(argv[1:])

        # encode each arg string to bytes if Python3
        color = COLOR_NAMES.get(option.color.lower()) if option.color else self._get_color(option.label)
        if color is None:
            stdout.write(b'Invalid color name: ' + _arg2bytes(option.color) + b'\n\n')
            stdout.write(parser.format_help().encode('utf-8'))
            parser.exit(2)

        self.prefix = self._make_prefix(option.label, color, option.separator)
        self.paths = [_arg2bytes(arg) for arg in args] or [None]
        return self

    @staticmethod
    def _get_color(label):
        index = 0
        for c in _arg2bytes(label):
            index = (index + (c if PY3 else ord(c))) % len(COLOR_SET)
        return COLOR_SET[index]

    @staticmethod
    def _make_prefix(label, color, separator):
        return (INVERSE + color + _arg2bytes(label) + RESET + _arg2bytes(separator) + RESET if label else b'') + color


def main(argv=sys.argv, stdin=_io2bytes(sys.stdin), stdout=_io2bytes(sys.stdout), stderr=_io2bytes(sys.stderr)):
    """
    Main function
    """
    setting = Setting().parse_args(stdout, argv)

    # Note: Do not use 'fileinput' module because it causes a buffering problem.
    try:
        for path in setting.paths:
            fh = stdin if path is None else io.open(path, 'rb', 0)
            try:
                for line in iter(fh.readline, b''):
                    stdout.write(setting.prefix + line + RESET)
                    stdout.flush()
            finally:
                if fh is not stdin:
                    fh.close()

    except Exception as e:
        stderr.write(('%s: %s\n' % (e.__class__.__name__, e)).encode('utf-8', 'ignore'))
        return 1

    return 0
