from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import errno

__all__ = ['PY3', 'arg2bytes', 'io2bytes', 'distribute', 'exception_handler']

PY3 = sys.version_info >= (3,)


def arg2bytes(arg):
    return os.fsencode(arg) if PY3 else arg


def io2bytes(fd):
    return fd.buffer if hasattr(fd, 'buffer') else fd


def distribute(num_workers, tasks):
    """
    Split tasks and distribute to each worker.

    :param num_workers: int
    :param tasks: list
    :return: [[task]] (list of the list of tasks)
    """
    assert 0 <= num_workers, 'num_workers must be non-negative integer.'

    ret = []
    if num_workers == 0:
        return ret

    quotient, extra = divmod(len(tasks), num_workers)
    j = 0
    for i in range(num_workers):
        k = quotient + (1 if i < extra else 0)
        ret.append(tasks[j:j + k])
        j += k
    return ret


#
# Decorators
#
def exception_handler(exception_func):
    def f(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                return 130
            except IOError as e:
                if e.errno == errno.EPIPE:
                    return 0
                else:
                    exception_func(e)
                    return 1
            except Exception as e:
                exception_func(e)
                return 1

        return wrapper
    return f
