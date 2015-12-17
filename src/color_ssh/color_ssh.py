from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import subprocess
from optparse import OptionParser

VERSION = 'color-ssh %s' % __import__('color_ssh').__version__

USAGE = """%prog [options...] [user@]hostname [command]"""


def __get_parser():
    p = OptionParser(version=VERSION, usage=USAGE)

    p.add_option(
        '--ssh', dest='ssh', default='ssh', type='string', metavar='SSH',
        help='override ssh command line string to SSH'
    )

    # todo: implement --host option
    # p.add_option(
    # '--host', dest='host', default=None, type='string', metavar='PATH',
    #     help='set path to host list to PATH'
    # )
    return p


def main(argv=sys.argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Main function
    """

    # parse args
    parser = __get_parser()
    option, args = parser.parse_args(argv[1:])

    ret = 1
    try:
        # todo: error check
        # todo: remove user name if exists
        host = args[0]

        proc_stdout = subprocess.Popen(['color-cat', '-l', host],
                                       stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        proc_stderr = subprocess.Popen(['color-cat', '-l', host, '-s', '+'],
                                       stdin=subprocess.PIPE, stdout=stdout, stderr=stderr)
        ret = subprocess.call(['ssh'] + args, stdin=stdin, stdout=proc_stdout.stdin, stderr=proc_stderr.stdin)

    except Exception as e:
        stdout.write(('\n%s: %s\n' % (e.__class__.__name__, e)).encode('utf-8', 'ignore'))

    return ret
