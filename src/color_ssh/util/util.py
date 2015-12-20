from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os

__all__ = ['PY3', 'arg2bytes', 'io2bytes']

PY3 = sys.version_info >= (3,)


def arg2bytes(arg):
    return os.fsencode(arg) if PY3 else arg


def io2bytes(fd):
    return fd.buffer if PY3 else fd
