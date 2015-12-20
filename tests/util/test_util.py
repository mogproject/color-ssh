from __future__ import division, print_function, absolute_import, unicode_literals

from mog_commons.unittest import TestCase
from color_ssh.util.util import distribute


class TestUtil(TestCase):
    def test_distribute(self):
        self.assertEqual(distribute(0, []), [])
        self.assertEqual(distribute(0, ['a']), [])
        self.assertEqual(distribute(1, []), [[]])
        self.assertEqual(distribute(1, ['a']), [['a']])
        self.assertEqual(distribute(1, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']),
                         [['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']])
        self.assertEqual(distribute(2, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']),
                         [['a', 'b', 'c', 'd'], ['e', 'f', 'g', 'h']])
        self.assertEqual(distribute(3, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']),
                         [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h']])
        self.assertEqual(distribute(5, ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']),
                         [['a', 'b'], ['c', 'd'], ['e', 'f'], ['g'], ['h']])
        self.assertEqual(distribute(5, ['a', 'b', 'c', 'd']),
                         [['a'], ['b'], ['c'], ['d'], []])

        xs = distribute(12345, range(200000))
        self.assertEqual(sum(map(sum, xs)), 200000 * (200000 - 1) / 2)

    def test_distribute_error(self):
        self.assertRaises(AssertionError, distribute, -1, [])
