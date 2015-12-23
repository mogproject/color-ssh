from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from color_ssh.util.util import exception_handler


class TestUtil(TestCase):
    def test_exception_handler(self):
        @exception_handler(lambda e: e)
        def f():
            raise KeyboardInterrupt

        self.assertEqual(f(), 130)
