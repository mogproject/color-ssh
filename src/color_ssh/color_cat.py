from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import io
from optparse import OptionParser
from color_ssh.setting.color import *

VERSION = 'color-cat %s' % __import__('color_ssh').__version__

USAGE = """%prog [options...] [file ...]"""


def __get_parser():
    p = OptionParser(version=VERSION, usage=USAGE)

    p.add_option(
        '-l', '--label', dest='label', default=b'', type='string', metavar='LABEL',
        help='set label name to LABEL'
    )
    p.add_option(
        '-c', '--color', dest='color', default=None, type='string', metavar='COLOR',
        help='set output color to COLOR (available colors: %s)' % ', '.join(sorted(COLOR_NAMES.keys()))
    )
    p.add_option(
        '-s', '--separator', dest='separator', default=b'|', type='string', metavar='SEPARATOR',
        help='set separator string to SEPARATOR (default: "|")'
    )
    return p


def get_color(label):
    index = 0
    for c in label:
        index = (index + ord(c)) % len(COLOR_SET)
    return COLOR_SET[index]


def make_prefix(label, color, separator):
    assert all(isinstance(param, bytes) for param in [label, color, separator])
    return (INVERSE + color + label + RESET + separator + RESET if label else b'') + color


def main(argv=sys.argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Main function
    """

    # parse args
    parser = __get_parser()
    option, args = parser.parse_args(argv[1:])
    color = COLOR_NAMES.get(option.color.lower()) if option.color else get_color(option.label)
    if color is None:
        stderr.write(('Invalid color name: %s\n\n' % option.color).encode('utf-8'))
        parser.print_help()
        return 2

    paths = args or [None]

    try:
        prefix = make_prefix(option.label, color, option.separator)

        # Note: Do not use 'fileinput' module. It causes a buffering issue.
        for path in paths:
            fh = stdin if path is None else io.open(path, 'rb', 0)
            try:
                for line in iter(fh.readline, b''):
                    stdout.write(prefix + line + RESET)
            finally:
                if fh is not stdin:
                    fh.close()

    except Exception as e:
        stderr.write(('%s: %s\n' % (e.__class__.__name__, e)).encode('utf-8', 'ignore'))
        return 1

    return 0
